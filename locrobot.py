import cv2
import numpy as np
import urllib2
import urllib
import math
import colorconfig
import time

def nothing(x):
    pass
    
xsize = 1000
ysize = 500
   
cap = cv2.VideoCapture(1)
cap.set(3,1000)
cap.set(4,500)
#cap.set(3,2000)
#cap.set(4,1200)

imgName = "Robot"
maskName = "Mask"

print(colorconfig.colorMat)
acx = [0] * 7
acy = [0] * 7
tc = [0] * 7


print "Starting..."
print "Fetching corner coordinates from server."

#Getting the corner coordinates from the server
req = urllib2.Request('http://tnk111.n7.se/getcorners.php')
response = urllib2.urlopen(req)
corners = response.read()
lines = corners.split('\n') 
cornerx1,cornery1 = lines[1].split(', ')
cornerx2,cornery2 = lines[2].split(', ')
cornerx3,cornery3 = lines[3].split(', ')
cornerx4,cornery4 = lines[4].split(', ')

print
#print "Online: Adjust the Robot-filter values to capture and log the position of the vehicle."
print "Press [ESCAPE] (with the image in focus) to quit."

cornerx = []
cornery = []

# Get first image from camera
_, frame = cap.read()
rows,cols,channels = frame.shape
# Create mask covering the area from the coordinates - and:ed with contour mask later on
nmask = np.zeros((rows,cols,1), np.uint8)
# Substract 5% from the topmost two y-coordinates 
mx1 = int(float(cornerx1))
mx2 = int(float(cornerx2))
mx3 = int(float(cornerx3))
mx4 = int(float(cornerx4))
my1 = int(float(cornery1)-0.05*rows)
my2 = int(float(cornery2)-0.05*rows)
my3 = int(float(cornery3))
my4 = int(float(cornery4))
a3 = np.array( [[[mx1,my1],[mx2,my2],
[mx3,my3],[mx4,my4]]], dtype=np.int32 )
cv2.fillPoly(nmask, a3, 255)

# Track the robot and store coordinates in database
skipFrame = 0
iter = 0
kernel = np.ones((3,3),np.uint8)
while(1):
    iter += 1

    # Take each frame
    _, frame = cap.read()

    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    font = cv2.FONT_HERSHEY_SIMPLEX

    for c in range(1,7):
        print colorconfig.colorName[c]
        lower = np.array([colorconfig.colorMat[c][0],colorconfig.colorMat[c][2],colorconfig.colorMat[c][4]])
        upper = np.array([colorconfig.colorMat[c][1],colorconfig.colorMat[c][3],colorconfig.colorMat[c][5]])
        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.erode(mask,kernel,iterations = 2)
        mask = cv2.dilate(mask,kernel,iterations = 2)
        if(c == 1):
            print "Adding "+colorconfig.colorName[0]
            lower = np.array([colorconfig.colorMat[0][0],colorconfig.colorMat[0][2],colorconfig.colorMat[0][4]])
            upper = np.array([colorconfig.colorMat[0][1],colorconfig.colorMat[0][3],colorconfig.colorMat[0][5]])
            mask2 = cv2.inRange(hsv, lower, upper)
            mask2 = cv2.erode(mask2,kernel,iterations = 2)
            mask2 = cv2.dilate(mask2,kernel,iterations = 2)
            mask = cv2.add(mask,mask2)

        # Clip the mask to the playfield area
        mask=cv2.bitwise_and(mask,mask,mask=nmask)
        contours, hierarchy = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

        cno = 0
        for cnt in contours:
            moments = cv2.moments(cnt)                          # Calculate moments
            if moments['m00']!=0:
                cnt = cv2.convexHull(cnt)
                cx = int(moments['m10']/moments['m00'])         # cx = M10/M00
                cy = int(moments['m01']/moments['m00'])         # cy = M01/M00
                cornerx.append(cx)
                cornery.append(cy)
                moment_area = moments['m00']                    # Contour area from moment
                contour_area = cv2.contourArea(cnt)             # Contour area using in_built function
                if contour_area > 5 and contour_area < 600:
                    cv2.drawContours(frame,[cnt],0,(80,255,80),1)   # draw contours in green color
                    cv2.circle(frame,(cx,cy),5,(0,0,0),-1)      # draw centroids in red color
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cv2.putText(frame, str((colorconfig.colorName[c],cx,cy)), (cx,cy), font, 0.5, (0,0,0), 1)
                    cno += 1
                    if iter == 1:
                        print "c: "+str(colorconfig.colorName[c])
                        acx[c] = cx
                        acy[c] = cy
                    tc[c] = time.time()    
                    acx[c] = 0.2*acx[c] + 0.8*cx
                    acy[c] = 0.2*acy[c] + 0.8*cy
                    print str(acx[c])+","+str(acy[c])




    skipFrame += 1
    if(skipFrame > 10):
        skipFrame = 0
        # Store cx and cy in database
        qp = ""
        for k in range(1,6):
            qp += str((str(tc[k])+","+str(acx[k])+","+str(acy[k])+";"))
        qp += str((str(tc[6])+","+str(acx[6])+","+str(acy[6])))
        req = urllib2.Request('http://tnk111.n7.se/set6robot.php?'+urllib.urlencode({'q':str(qp)}))
        response = urllib2.urlopen(req)
        print "Robot red coordinate ("+str(acx[1])+", "+str(acy[1])+") at "+str(time.time())+" uploaded with status: "+str(response.read())
#        cv2.circle(frame,(int(acx),int(acy)),5,(255,0,0),-1)      # draw centroid in blue color

    cv2.line(frame,(int(float(cornerx1)),int(float(cornery1))),(int(float(cornerx2)),int(float(cornery2))),(255,0,0),1)
    cv2.line(frame,(int(float(cornerx2)),int(float(cornery2))),(int(float(cornerx3)),int(float(cornery3))),(255,0,0),1)
    cv2.line(frame,(int(float(cornerx3)),int(float(cornery3))),(int(float(cornerx4)),int(float(cornery4))),(255,0,0),1)
    cv2.line(frame,(int(float(cornerx4)),int(float(cornery4))),(int(float(cornerx1)),int(float(cornery1))),(255,0,0),1)

    cv2.imshow(imgName,frame)
#    cv2.imshow(imgName,mask2)


    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()
