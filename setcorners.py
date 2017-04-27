import cv2
import numpy as np
import urllib2
import urllib
import math
import colorconfigcorners

# Sort the coordinates in CCW order, starting with SW
def sortcoords(x, y):
    cx = 1.0*sum(x)/4
    cy = 1.0*sum(y)/4

    xcoords = ([tx-cx for tx in x])
    ycoords = ([ty-cy for ty in y])
    angles = []
    for i in range(0,4):
        angles.append(180+180/math.pi*math.atan2(ycoords[i], xcoords[i]))

    sortargs = np.argsort(angles)

    return [(x[i],y[i]) for i in sortargs]


def nothing(x):
    pass
    
    
cap = cv2.VideoCapture(1)
cap.set(3,1000)
cap.set(4,500)

sliderName = "Thresholds"
imgName = "Robot"
maskName = "Mask"

cv2.namedWindow(sliderName, cv2.CV_WINDOW_AUTOSIZE)
#cv2.namedWindow(sliderName)

cv2.createTrackbar('Corner H',sliderName,colorconfigcorners.corner_h,255,nothing)
cv2.createTrackbar('Corner S',sliderName,colorconfigcorners.corner_s,255,nothing)
cv2.createTrackbar('Corner V',sliderName,colorconfigcorners.corner_v,255,nothing)
cv2.createTrackbar('Corner H2',sliderName,colorconfigcorners.corner_h2,255,nothing)
cv2.createTrackbar('Corner S2',sliderName,colorconfigcorners.corner_s2,255,nothing)
cv2.createTrackbar('Corner V2',sliderName,colorconfigcorners.corner_v2,255,nothing)

#cv2.resizeWindow("Thresholds",400,200)

print "Setcorner: Identify tennis ball corner points. Adjust Corner-filter to capture their positions."
print "Press [ESCAPE] (with the image in focus) when ready to store the corner points at the positioning server."

cornerx = []
cornery = []

ascoordsx = [0 for x in range(0,4)]
ascoordsy = [0 for x in range(0,4)]



while(1):

    h = cv2.getTrackbarPos('Corner H',sliderName)
    s = cv2.getTrackbarPos('Corner S',sliderName)
    v = cv2.getTrackbarPos('Corner V',sliderName)
    h2 = cv2.getTrackbarPos('Corner H2',sliderName)
    s2 = cv2.getTrackbarPos('Corner S2',sliderName)
    v2 = cv2.getTrackbarPos('Corner V2',sliderName)

#    print str(h)+" "+str(s)+" "+str(v)

    # Take each frame
    _, frame = cap.read()

    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # define range of blue color in HSV
    lower = np.array([h,s,v])
    upper = np.array([h2,s2,v2])

    # Threshold the HSV image to get the robot position
    rmask = cv2.inRange(hsv, lower, upper)

    kernel = np.ones((3,3),np.uint8)
    rmask = cv2.erode(rmask,kernel,iterations = 2)
    kernel = np.ones((3,3),np.uint8)
    rmask = cv2.dilate(rmask,kernel,iterations = 3)

    font = cv2.FONT_HERSHEY_SIMPLEX
    contours, hierarchy = cv2.findContours(rmask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    if(len(contours) > 4):
        cv2.putText(frame, "Too many contours, adjust color filter please.", (20,30), font, 0.8, (255,255,255), 1)
    if(len(contours) < 4):
        cv2.putText(frame, "Too few contours, adjust color filter please.", (20,30), font, 0.8, (255,255,255), 1)

    cno = 0
 
    cornerx = []
    cornery = [] 
    for cnt in contours:
        moments = cv2.moments(cnt)                          # Calculate moments
        if moments['m00']!=0:
            cx = int(moments['m10']/moments['m00'])         # cx = M10/M00
            cy = int(moments['m01']/moments['m00'])         # cy = M01/M00
            moment_area = moments['m00']                    # Contour area from moment
            contour_area = cv2.contourArea(cnt)             # Contour area using in_built function
            if contour_area > 25:
                cv2.drawContours(frame,[cnt],0,(0,255,0),1)   # draw contours in green color
                cv2.circle(frame,(cx,cy),5,(0,0,255),-1)      # draw centroids in red color
                cv2.putText(frame, str((cx,cy)), (cx,cy), font, 0.5, (255,255,255), 1)
                cornerx.append(cx)
                cornery.append(cy)
                cno += 1
    cv2.putText(frame, "Corners: "+str(len(cornerx)), (20,50), font, 0.5, (255,255,255),1)

    if (len(cornerx) == 4):

        scoords = sortcoords(cornerx, cornery)

        cv2.line(frame,(scoords[0][0],scoords[0][1]),(scoords[1][0],scoords[1][1]),(255,255,255),1)
        cv2.line(frame,(scoords[1][0],scoords[1][1]),(scoords[2][0],scoords[2][1]),(255,255,255),1)
        cv2.line(frame,(scoords[2][0],scoords[2][1]),(scoords[3][0],scoords[3][1]),(255,255,255),1)
        cv2.line(frame,(scoords[3][0],scoords[3][1]),(scoords[0][0],scoords[0][1]),(255,255,255),1)

        ascoordsx=[(ascoordsx[i] + 0.1*(scoords[i][0]-ascoordsx[i])) for i in range(0,4)]
        ascoordsy=[(ascoordsy[i] + 0.1*(scoords[i][1]-ascoordsy[i])) for i in range(0,4)]

    cv2.line(frame,(int(ascoordsx[0]),int(ascoordsy[0])),(int(ascoordsx[1]),int(ascoordsy[1])),(255,0,0),1)
    cv2.line(frame,(int(ascoordsx[1]),int(ascoordsy[1])),(int(ascoordsx[2]),int(ascoordsy[2])),(255,0,0),1)
    cv2.line(frame,(int(ascoordsx[2]),int(ascoordsy[2])),(int(ascoordsx[3]),int(ascoordsy[3])),(255,0,0),1)
    cv2.line(frame,(int(ascoordsx[3]),int(ascoordsy[3])),(int(ascoordsx[0]),int(ascoordsy[0])),(255,0,0),1)

    cv2.imshow(imgName,frame)

#    cv2.imshow(maskName,rmask)

    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

if (ascoordsx[0]>0):
    print "The following corner points are identified and stored:"
    print "("+str(ascoordsx[0])+", "+str(ascoordsy[0])+")"
    print "("+str(ascoordsx[1])+", "+str(ascoordsy[1])+")"
    print "("+str(ascoordsx[2])+", "+str(ascoordsy[2])+")"
    print "("+str(ascoordsx[3])+", "+str(ascoordsy[3])+")"

    # Upload the corner points to the database
    ascoords = (ascoordsx[0], ascoordsy[0], ascoordsx[1], ascoordsy[1], ascoordsx[2], ascoordsy[2], ascoordsx[3], ascoordsy[3])

#    handler=urllib2.HTTPHandler(debuglevel=1)
#    opener = urllib2.build_opener(handler)
#    urllib2.install_opener(opener)

    print str(ascoords)

    req = urllib2.Request('http://tnk111.n7.se/setcorners.php?'+urllib.urlencode({'q':str(ascoords)}) )
    response = urllib2.urlopen(req)
    print "Corner coordinates uploaded with status: "+str(response.read())
else:
    print "Error: No corner points were identified or uploaded. Terminating."
    cv2.destroyAllWindows()
    exit(0)

cv2.destroyAllWindows()
