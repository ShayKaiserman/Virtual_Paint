# STEP 1 - capture video from computer camera.
# STEP 2 - choose a color to draw with.
# STEP 3 - imply a mask with the same color, to detect our marker.
# STEP 4 - detect the contours of the marker and define his "paint point".
# STEP 5 - draw on the screen with the same color.

import cv2
import PILasOPENCV as PIL
from PILasOPENCV import Image
import pandas as pd
import numpy as np

# ---- functions -----

# color recognition function
def recognize_color(R,G,B):
    minimum = 10000
    # going through all the colors in the table and grading
    # the matching between their RGB values and ours' input
    # in the end the chosen color is the one that gives us the minimum difference

    for i in range(len(csv)):
        d = abs(R- int(csv.loc[i,"R"])) + abs(G- int(csv.loc[i,"G"]))+ abs(B- int(csv.loc[i,"B"]))
        if(d<=minimum):
            minimum = d
            cname = csv.loc[i,"color_name"]
    return cname

# function to define what happens in double-click event -
# we get the pixel location and his RGB values
def mouse_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        global b,g,r,xpos,ypos, clicked
        clicked = True
        xpos = x
        ypos = y
        b,g,r = img[y,x]
        b = int(b)
        g = int(g)
        r = int(r)

def findColor(img, myColor, ColorValue):

    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    newPoints = []
    lower = np.array(myColor[0:3])
    upper = np.array(myColor[3:6])
    mask = cv2.inRange(imgHSV, lower, upper)
    x, y = getContours(mask)
    cv2.circle(imgResult, (x, y), 15, ColorValue, cv2.FILLED)
    if x != 0 and y != 0:
        newPoints.append([x, y, ColorValue])

    # cv2.imshow(str(myColor[0]), mask)

    return newPoints

# function to get the contours in a certain image
# return the middle of the contour (the "paint point")
def getContours(img):
    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    x, y, w, h = 0, 0, 0, 0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 100:
            # cv2.drawContours(imgResult, cnt, -1, (255, 0, 0), 3)
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            x, y, w, h = cv2.boundingRect(approx)
            # drawing all the contours in blue (width of 3)
            cv2.drawContours(imgResult, cnt, -1, (255, 0, 0), 3)
    return x + w // 2, y

# function to keep memory of all the points that have been drawn
def drawOnCanvas(myPoints):
    count_points = 0
    for point in myPoints:
        cv2.circle(imgResult, (point[0], point[1]), 4, point[2], cv2.FILLED)
        count_points += 1
        print(point)
        # drawing a line between the points (only if them with the same color),
        # and starting when we have at least two points
        if count_points > 1:
            if point[2] == myPoints[count_points-2][2]:
                cv2.line(imgResult, (point[0], point[1]), (myPoints[count_points-2][0], myPoints[count_points-2][1]),
                     point[2], 6)


# ---- main script -----

# import csv file with RGB definition of more than 800 different colors
path = "Resources\color-names-master\output\colors.csv"
index = ["color", "color_name", "hex", "R", "G", "B"]
csv = pd.read_csv(path, names=index, header=None)

# define default for global variables
clicked = False
r = g = b = xpos = ypos = 0

# create a window to draw on
cv2.namedWindow('Virtual Paint')
# we would detect mouse click only on that window
cv2.setMouseCallback('Virtual Paint', mouse_click)

myPoints = []  ## [x , y , colorId ]

# STEP 1

# cap = cv2.VideoCapture(1)
cap = cv2.VideoCapture(0) # using the default main camera

# cap.set(3,640) # set window width
# cap.set(4,480) # set window height

while True:
    success, img = cap.read()

    # making copies of the image, that we can work on
    img_copy = img.copy()
    imgResult = img.copy()

# STEP 2 (only if we clicked on the screen) - choose and recognize color
    if (clicked):
        # display chosen color's name
        text = recognize_color(r,g,b)
        cv2.putText(img_copy, text, (xpos,ypos),2,0.6,
                    (r,g,b),2)

# STEP 3 +4 - imply a mask of the chosen color

        color = np.uint8([[[b,g,r]]])
        hsv_color = cv2.cvtColor(color, cv2.COLOR_BGR2HSV)
        imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hsv_color_array = hsv_color[0][0]

        # define parameter to adjust lower and upper boundries (between 0 to 255)
        bound_param = 30

        lower = np.array([hsv_color_array[0]-bound_param,hsv_color_array[1]-bound_param,hsv_color_array[2]-bound_param])
        upper = np.array([hsv_color_array[0]+bound_param,hsv_color_array[1]+bound_param,hsv_color_array[2]+bound_param])
        myColor = np.concatenate((lower, upper))
        ColorValue = [b, g, r]
        newPoints = findColor(img, myColor, ColorValue)

# STEP 5 - drawing

        if len(newPoints) != 0:
            for newP in newPoints:
                myPoints.append(newP)
        if len(myPoints) != 0:
            drawOnCanvas(myPoints)

        cv2.imshow("Result", imgResult)

    cv2.imshow('Virtual Paint', img_copy)

    k = cv2.waitKey(1)
    if k == ord('b'):
        break

