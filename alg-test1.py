import cv2 as cv
import os
import numpy as np
import time
import scipy
cv2=cv
DBG_TIMER = 0
DBG=False
if DBG:
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
else:
    def dbg_timer(msg):
        pass
    def dbg_timer_rst():
        pass
def mid(follow, mask,final):
    """
        计算图像中车道的中点。

    参数：
            follow （numpy.ndarray）：包含车道的图像。
            mask （numpy.ndarray）：通道的二进制掩码。
            final （numpy.ndarray）：包含车道的图像。(BGR)

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
    failCnt=0
    failCntTotal=[0,0]
    flags={
        "CROSSING":None,
    }
    for y in range(follow.shape[0] - 1, -1, -1):
        dbg_timer_rst()
        left=0
        right=follow.shape[1]
        # 计算左边界
        fail=0
        if (mask[y][0:half] == np.zeros_like(mask[y][0:half])).all():
            left = max(0, half - halfWidth)
            fail=1
            failCntTotal[0]+=1
        else:
            left_indices = np.where(mask[y][0:half] == 255)[0]
            if left_indices.size > 0:
                left = np.average(left_indices)
            else:
                left = 0  # 或者选择一个合理的默认值
                fail=1
                failCntTotal[0]+=1
            #print("Left", left)
        dbg_timer("left")
        # 计算右边界
        if (mask[y][half:min(follow.shape[1], half + halfWidth)] == np.zeros_like(mask[y][half:min(follow.shape[1], half + halfWidth)])).all():
            right = min(follow.shape[1], half + halfWidth)
            fail=1
            failCntTotal[1]+=1
        else:
            right_indices = np.where(mask[y][half:follow.shape[1]] == 255)[0]
            if right_indices.size > 0:
                right = np.average(right_indices) + half
            else:
                right = follow.shape[1]  # 或者选择一个合理的默认值
                fail=1
                failCntTotal[1]+=1
            #print("Right", right)
        dbg_timer("right")
        if fail==0:
            mid = (left + right) // 2  # 计算拟合中点
            #print(left,right,half,mid)
            half = int(mid)  # 递归,从下往上确定分割线
            follow[y, int(mid)] = 255  # 画出拟合中线
            final[y, int(mid)] = (0, 0, 255)  # 画出拟合中线
            mids.append(mid)
        else:
            if len(mids)>0:
                mids.append(mids[-1])
            else:
                mids.append(half)
            follow[y, int(mids[-1])] = 128  # 画出拟合中线
            final[y, int(mids[-1])] = (0, 0, 128)
        failCnt+=fail
        #print("Mid", mid)
        # if y == 360:  # 设置指定提取中点的纵轴位置
        #     mid_output = int(mid)

    #cv.circle(follow, (mid_output, 360), 5, 255, -1)  # opencv为(x,y),画出指定提取中点
    mids = scipy.signal.savgol_filter(mids, 11, 3, mode="nearest")
    for i in range(len(mids)):
        final[int(follow.shape[0] - 1 - i), int(mids[i])] = (255, 0, 0)  # 画出拟合中线(经过滤波)
    error = np.average(np.array(mids)) - halfWidth
    cv2.putText(follow, f"error:{error}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255), 2, cv2.LINE_4)
    
    
    flags["CROSSING"]=failCnt>int(follow.shape[0]*.9)
    flags["ERROR"]=error
    flags["NOT_ALL_BLACK"]=failCnt<int(follow.shape[0]*.99)
    flags["FAILCNTS"]=failCntTotal
    
    flags["L_VAILD"]=failCntTotal[0]<int(follow.shape[0]*.9)
    flags["R_VAILD"]=failCntTotal[1]<int(follow.shape[0]*.9)

    flags["CHAOS_VAR"]=np.var(mids)
    flags["NOT_CHAOS"]=flags["CHAOS_VAR"]<=4000
    
    flags["D_VAILD"]=flags["NOT_ALL_BLACK"] and flags["NOT_CHAOS"]
    cv2.putText(final, f"flags{flags}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2, cv2.LINE_4)
    return follow, error,final,flags  # error为负数偏右,正数偏左
 
 
n = -1
# 存放图片的文件夹路径
path = "./phone"
DOWNV=np.array((15,20,180))
UPV=np.array((50,255,255))
cap=cv.VideoCapture(0)
while True:
    os.system("cls")
    stt=time.time()
    ret,img = cap.read()
    if not ret:
        print("\033[1;31;40m======\nError: Camera Error\n======\n\033[0m")
        break
        
    img = cv.resize(img,(640,480))
    
    # HSV阈值分割(颜色)
    img_hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    mask = cv.inRange(img_hsv, DOWNV, UPV)
    #mask2=cv.inRange(img_hsv, np.array((0,0,254)), np.array((1,1,255)))
    #mask=cv.bitwise_or(mask,mask2)
    # 高斯模糊(去除噪声)
    mask = cv2.GaussianBlur(mask,(5,5),0)

    follow = mask.copy()
    follow, error,final,flags = mid(follow, mask,img)
    
    print(n, f"error:{error}",f"flags:{flags}")
    cv2.putText(follow, f"FPS:{1/(time.time()-stt)}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255), 2, cv2.LINE_4)
    #cv.imshow("img", img)
    cv.imshow("follow", follow)
    cv2.imshow("final", img)
    if(cv.waitKey(1) & 0xFF == ord('q') or cv.waitKey(1) & 0xFF == ord('Q')):
        break
    
cv.destroyAllWindows()