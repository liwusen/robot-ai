import cv2 as cv
import os
import numpy as np,time
import scipy
cv2=cv

def mid(follow, mask):
    """
    Calculates the midpoint of the lane in an image.

    Args:
        follow (numpy.ndarray): The image containing the lane.
        mask (numpy.ndarray): The binary mask of the lane.

    Returns:
        tuple: A tuple containing the modified image with the lane midpoint marked and the error value.

    The function iterates through the image from bottom to top, finding the midpoint of the lane at each row.
    It uses the binary mask to determine the left and right boundaries of the lane at each row.
    The midpoint is calculated as the average of the left and right boundaries.
    The function also calculates the error, which represents the deviation of the midpoint from the center of the image.
    The modified image is returned with the lane midpoint marked, along with the error value.
    """
    halfWidth = follow.shape[1] // 2
    half = halfWidth  # 从下往上扫描赛道,最下端取图片中线为分割线
    mids = []
    for y in range(follow.shape[0] - 1, -1, -3):
        left=0
        right=follow.shape[1]
        # 计算左边界
        if (mask[y][0:half] == np.zeros_like(mask[y][0:half])).all():
            left = max(0, half - halfWidth)
        else:
            left_indices = np.where(mask[y][0:half] == 255)[0]
            if left_indices.size > 0:
                left = np.average(left_indices)
            else:
                left = 0  # 或者选择一个合理的默认值
            #print("Left", left)

        # 计算右边界
        if (mask[y][half:min(follow.shape[1], half + halfWidth)] == np.zeros_like(mask[y][half:min(follow.shape[1], half + halfWidth)])).all():
            right = min(follow.shape[1], half + halfWidth)
        else:
            right_indices = np.where(mask[y][half:follow.shape[1]] == 255)[0]
            if right_indices.size > 0:
                right = np.average(right_indices) + half
            else:
                right = follow.shape[1]  # 或者选择一个合理的默认值
            #print("Right", right)

        mid = (left + right) // 2  # 计算拟合中点
        #print(left,right,half,mid)
        half = int(mid)  # 递归,从下往上确定分割线
        follow[y, int(mid)] = 255  # 画出拟合中线
        mids.append(mid)

        # if y == 360:  # 设置指定提取中点的纵轴位置
        #     mid_output = int(mid)

    #cv.circle(follow, (mid_output, 360), 5, 255, -1)  # opencv为(x,y),画出指定提取中点
    mids = scipy.signal.savgol_filter(mids, 11, 3, mode="nearest")
    error = np.average(np.array(mids)) - halfWidth
    cv2.putText(follow, f"error:{error}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255), 2, cv2.LINE_4)
    return follow, error  # error为负数偏右,正数偏左
 
 
n = -1
# 存放图片的文件夹路径
path = "./phone"
DOWNV=np.array((15,20,180))
UPV=np.array((50,255,255))

while True:
    stt=time.time()
    ret,img = cv.VideoCapture(0).read()
    if not ret:
        continue
    img = cv.resize(img,(640,480))
    
    # HSV阈值分割
    img_hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    mask = cv.inRange(img_hsv, DOWNV, UPV)
    mask = cv2.GaussianBlur(mask,(5,5),0)
    follow = mask.copy()
    follow, error = mid(follow, mask)
    print(n, f"error:{error}")
    
    cv.imshow("img", img)
    cv.imshow("mask", mask)
    cv.imshow("follow", follow)
    if(cv.waitKey(1) & 0xFF == ord('q') or cv.waitKey(1) & 0xFF == ord('Q')):
        break
    print("FPS=",1/(time.time()-stt))
cv.destroyAllWindows()