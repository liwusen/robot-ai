import cv2 as cv
import os
import numpy as np
import time
import scipy
cv2=cv
DBG_TIMER = 0
def dbg_timer(msg):
    global DBG_TIMER
    if DBG_TIMER == 0:
        print(msg)
    else:
        print(msg, time.time() - DBG_TIMER)
    DBG_TIMER = time.time()
def dbg_timer_rst():
    global DBG_TIMER
    DBG_TIMER = time.time()
    print("=====DBG_TIMER reset=====")
def mid(follow, mask):
    """
        计算图像中车道的中点。

    参数：
            follow （numpy.ndarray）：包含车道的图像。
            mask （numpy.ndarray）：通道的二进制掩码。

    返回：
            tuple：包含标记了车道中点和错误值的修改图像的元组。

    该函数从下到上遍历图像，在每一行处找到车道的中点。
        它使用二进制掩码来确定每行车道的左右边界。
        中点计算为左右边界的平均值。
        该函数还计算误差，该误差表示中点与图像中心的偏差。
        将返回修改后的图像，并标记车道中点以及错误值。
    """
    
    halfWidth = follow.shape[1] // 2
    half = halfWidth  # 从下往上扫描赛道,最下端取图片中线为分割线
    mids = []
    for y in range(follow.shape[0] - 1, -1, -3):
        dbg_timer_rst()
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
        dbg_timer("left")
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
        dbg_timer("right")
        mid = (left + right) // 2  # 计算拟合中点
        #print(left,right,half,mid)
        half = int(mid)  # 递归,从下往上确定分割线
        follow[y, int(mid)] = 255  # 画出拟合中线
        mids.append(mid)
        #print("Mid", mid)
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
cap=cv.VideoCapture(0)
while True:
    stt=time.time()
    ret,img = cap.read()
    if not ret:
        continue
    img = cv.resize(img,(640,480))
    
    # HSV阈值分割(颜色)
    img_hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    mask = cv.inRange(img_hsv, DOWNV, UPV)

    # 高斯模糊(去除噪声)
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