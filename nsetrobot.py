import cv2
import numpy as np
import urllib2
import urllib
import math
import colorconfig
import datetime

def sliderCallback():
    pass
    
# Robot coordinates, smoothed
acx = 0
acy = 0

# Flatfield coordinates
cornerx = []
cornery = []

skipFrame = 0
iter = 0

# Suggested size of video image, actual size depends on camera ratio
xsize = 1000
ysize = 500
   
# Init external camera
cap = cv2.VideoCapture(1)
cap.set(3, xsize)
cap.set(4, ysize)

# Name windows
sliderName = "Thresholds"
imgName = "Robot"
maskName = "Mask"

#cv2.namedWindow(sliderName, cv2.CV_WINDOW_AUTOSIZE)
cv2.namedWindow(sliderName)

print "Starting..."
print "Fetching corner coordinates from server."

# Getting the corner coordinates from the server
req = urllib2.Request('http://tnk111.n7.se/getcorners.php')
response = urllib2.urlopen(req)
corners = response.read()
lines = corners.split('\n') 
cornerx1,cornery1 = lines[1].split(', ')
cornerx2,cornery2 = lines[2].split(', ')
cornerx3,cornery3 = lines[3].split(', ')
cornerx4,cornery4 = lines[4].split(', ')

print
print "Online: Adjust the Robot-filter values to capture and log the position of the vehicle."
print "Press [ESCAPE] (with the image in focus) to quit."


# Create trackbars for color change
cv2.createTrackbar('Robot H',sliderName,colorconfig.robot_h,255,sliderCallback)
cv2.createTrackbar('Robot S',sliderName,colorconfig.robot_s,255,sliderCallback)
cv2.createTrackbar('Robot V',sliderName,colorconfig.robot_v,255,sliderCallback)
cv2.createTrackbar('Robot H2',sliderName,colorconfig.robot_h2,255,sliderCallback)
cv2.createTrackbar('Robot S2',sliderName,colorconfig.robot_s2,255,sliderCallback)
cv2.createTrackbar('Robot V2',sliderName,colorconfig.robot_v2,255,sliderCallback)


# Track the robot and store coordinates in database

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


while(1):
    iter += 1

    # Get slides values
    h = cv2.getTrackbarPos('Robot H',sliderName)
    s = cv2.getTrackbarPos('Robot S',sliderName)
    v = cv2.getTrackbarPos('Robot V',sliderName)
    h2 = cv2.getTrackbarPos('Robot H2',sliderName)
    s2 = cv2.getTrackbarPos('Robot S2',sliderName)
    v2 = cv2.getTrackbarPos('Robot V2',sliderName)

    # Take each frame
    _, frame = cap.read()

    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Set up color filter based on the slider values
    lower = np.array([h,s,v])
    upper = np.array([h2,s2,v2])
    rmask = cv2.inRange(hsv, lower, upper)

    # Erode and dilate the mask image
    kernel = np.ones((3,3),np.uint8)
    rmask = cv2.erode(rmask,kernel,iterations = 2)
    kernel = np.ones((3,3),np.uint8)
    rmask = cv2.dilate(rmask,kernel,iterations = 2)

    # Clip the mask to the playfield area
    rmask=cv2.bitwise_and(rmask,rmask,mask=nmask)

    font = cv2.FONT_HERSHEY_SIMPLEX
    contours, hierarchy = cv2.findContours(rmask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    # Write info on the number of contours found
#    if(len(contours) > 1):
#        cv2.putText(frame, "Too many contours, adjust color filter please.", (20,30), font, 0.8, (255,255,255), 1)
#    if(len(contours) < 1):
#        cv2.putText(frame, "Too few contours, adjust color filter please.", (20,30), font, 0.8, (255,255,255), 1)

    cno = 0
    for cnt in contours:
        moments = cv2.moments(cnt)                          # Calculate moments
        if moments['m00']!=0:
            cx = int(moments['m10']/moments['m00'])         # cx = M10/M00
            cy = int(moments['m01']/moments['m00'])         # cy = M01/M00
            cornerx.append(cx)
            cornery.append(cy)
            moment_area = moments['m00']                    # Contour area from moment
            contour_area = cv2.contourArea(cnt)             # Contour area using in_built function
            
            if contour_area > 1:
                cv2.drawContours(frame,[cnt],0,(0,255,0),1)   # draw contours in green color
                cv2.circle(frame,(cx,cy),5,(0,0,255),-1)      # draw centroids in red color
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(frame, str((cx,cy)), (cx,cy), font, 0.5, (255,255,255), 1)
                cno += 1
                if iter == 1:
                    acx = cx
                    acy = cy
                acx = 0.2*acx + 0.8*cx
                acy = 0.2*acy + 0.8*cy
            
    # Upload coordinate if only one point is found (good?)
    if(cno == 1):
        skipFrame += 1
        # Skip some uploads to lower the server stress
        if(skipFrame > 1):
            skipFrame = 0
            # Store cx and cy in database
            req = urllib2.Request('http://tnk111.n7.se/setrobot.php?'+urllib.urlencode({'q':str(str(acx)+","+str(acy))}) )
            response = urllib2.urlopen(req)
            print "Robot coordinate ("+str(acx)+", "+str(acy)+") at "+str(datetime.datetime.now())+" uploaded with status: "+str(response.read())
            cv2.circle(frame,(int(acx),int(acy)),5,(255,0,0),-1)      # draw centroid in blue color

    # Draw the playfield in blue on the frame image
    cv2.line(frame,(int(float(cornerx1)),int(float(cornery1))),(int(float(cornerx2)),int(float(cornery2))),(255,0,0),1)
    cv2.line(frame,(int(float(cornerx2)),int(float(cornery2))),(int(float(cornerx3)),int(float(cornery3))),(255,0,0),1)
    cv2.line(frame,(int(float(cornerx3)),int(float(cornery3))),(int(float(cornerx4)),int(float(cornery4))),(255,0,0),1)
    cv2.line(frame,(int(float(cornerx4)),int(float(cornery4))),(int(float(cornerx1)),int(float(cornery1))),(255,0,0),1)

    # Show the video feed with graphical overlays
    cv2.imshow(imgName,frame)

    # Stop the camera feed when [Esc] is pressed
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()
