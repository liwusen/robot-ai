import cv2,math,scipy
import numpy as np
cap=cv2.VideoCapture(0)
def circleFunc(x):
    #⁅𝑦=√(1−𝑥^2 )⁆
    return math.sqrt(abs(1-x*x))
UPV=np.array((15,20,180))
DOWNV=np.array((50,255,255))
nowMid=0
CONF_filtrationMin=20
def mid(mask,follow):
    halfWidth= follow.shape[1] // 2
    half = halfWidth
    height=mask.shape[0]
    width=mask.shape[1]
    mids=[]
    left=0
    right=1
    mid=0
    half=0
    for y in range(height - 1, -1, -1):
        if (mask[y][max(half-halfWidth,0):half]==np.zeros_like(mask[y][max(half-halfWidth,0):half])).all():
            left=max(half-halfWidth,0)
        else:
            left=np.average(np.where(mask[y][0:half])==255)
        if(mask[y][half:min(width,half+halfWidth)]==np.zeros_like(mask[y][half:min(width,half+halfWidth)])).all():
            right=min(half+halfWidth,width)
        else:
            right=np.average(np.where(mask[y][half:width]==255))+half
        print(left,right)
        mid=(left+right)//2
        print(half,mid)
        half=int(mid)
        
        mids.append(mid)
    mids=scipy.signal.savgol_filter(mids,11,3,mode="nearest")
    for i,j in enumerate(mids):
        cv2.circle(follow,(height-i,j),5,(0,0,255),-1)
    error=np.average(np.array(mids))
    return error
        
        
    
while True:
    ret, frame = cap.read()
    if(not ret): continue


    height, width = frame.shape[:2]
    gray_img=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    hsv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    print("HSV:",hsv_img[100][100])
    threshold_img = cv2.inRange(hsv_img, UPV, DOWNV)
    threshold_img = cv2.GaussianBlur(threshold_img,(5,5),0)
    cv2.imshow('threshold', threshold_img)
    error,final=mid(threshold_img,frame[:])
    cv2.line(final,(width//2,0),(width//2,height),(255,255,0),3)
    cv2.imshow('final', final)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break