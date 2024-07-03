import cv2,math
cap=cv2.VideoCapture(0)
def circleFunc(x):
    #⁅𝑦=√(1−𝑥^2 )⁆
    return math.sqrt(abs(1-x*x))

while True:
    ret, frame = cap.read()
    height, width = frame.shape[:2]
    cv2.imshow('CAMERA', frame)
    
    if ret:
        gray_img=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #print(gray_img[100][100])
        #cv2.imshow('gray', gray_img)
        retval,threshold_img = cv2.threshold(gray_img,180,255,cv2.THRESH_BINARY)
        
        cv2.imshow('threshold', threshold_img)
        final=frame[:]
        left=0
        right=1
        last100_x=[0 for i in range(100)]
        last_x=0
        crossingFlg=False
        crossingLineY=0
        for i in range(height-1,0,-3):
            for j in range(width//2, width,3):
                if(threshold_img[i][j]>=240):
                    right=j
                    break
            for j in range(width//2, 0, -3):
                if(threshold_img[i][j]>=240):
                    left=j
                    break
            if(left<70): left=70
            #print("left",left)
            if(right>650): right=650
            if(left<right):
                #print("T1",(left+right+last100_x[80]*0.8)//2.8)
                cv2.line(final, (last_x, i-5),
                          (int((left+right+last100_x[80]*0.5+last100_x[70]*0.4+last100_x[50]*0.3)//3.2),i),(0, 255, 0), 
                        2)
                last_x=(left+right)//2
            last100_x=last100_x[1:]+[(left+right)//2]
            if(True and i>=height//2):
                #十字路口判断
                if(threshold_img[i][width//2]>=240):
                    cv2.line(final, (width//2, height//2), (width//2, i), (0, 255, 0), 2)
                    crossingFlg=True
                    crossingLineY=i
                    break
                
            

        
        if crossingFlg:
            cv2.putText(final, 'Crossing', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            nowx,nowy=right,crossingLineY
            
            slope=(last100_x[0]-last100_x[50])/50
            #斜率 （平均到每像素）
            #
            #print("SLOPE:",slope)
            lx,rx=left,right
            for i in range(crossingLineY-300,crossingLineY+300):
                lx=lx+slope
                lx=int(lx)
                if(lx<0 or lx>=width  or i>=height):
                    continue
                #print("FULL",lx,i)
                final[i][lx]=(255,0,0)
            rightRotate=cv2.rotate(threshold_img,cv2.ROTATE_90_CLOCKWISE)[:]
            leftRotate=cv2.rotate(threshold_img,cv2.ROTATE_90_COUNTERCLOCKWISE)[:]
            rightPre=cv2.rotate(frame,cv2.ROTATE_90_CLOCKWISE)[:]
            #右判断
            
            alpha=.25
            for i in range(0,width,3):
                crossingData=[[0,0],[0,0]]
                print("exec")
                for j in range(int(height*alpha),height,3):
                    if(rightRotate[i][j]>=240):
                        crossingData[1][1]=j#left
                for j in range(int(height*alpha),0,-3):
                    if(rightRotate[i][j]>=240):
                        crossingData[1][0]=j#right
                cv2.circle(final,(i,crossingData[1][0]),5,(0,0,255),-1)
                cv2.circle(rightPre,(i,crossingData[1][0]),5,(0,0,255),-1)
                print("RIGHT",i,(crossingData[1][1]+crossingData[1][0])//2)
            cv2.imshow('rightRotatePreview', rightPre)
            # while(nowx<width and nowy<height):
            #     for i2 in range(4,6,1):
            #         i=i2/10
            #         tx=nowx+i
            #         ty=circleFunc(tx)
            #         tx,ty=int(tx),int(ty)
            #         if(tx>=width or ty>=height):
            #             break
            #         if(threshold_img[tx][ty]>=240):
            #             nowx=tx
            #             nowy=ty
            #             final[tx][ty]=(255,0,0)
            #             break
            #     else:
            #         break
        cv2.line(final,(width//2,0),(width//2,height),(255,255,0),3)
        cv2.imshow('final', final)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break