#####################################################################
# Name: trackColorLeftCenterRight.py
# 
# Authors:  Patrick Bell
# Creation Date: 10-26-18
# Update Date:
# 
# Description: Tracks a predetermined color (green) and outs to the screen
# if it is to the left, right, or in the center of the screen.
# It can take a sys argument of a HSV color.
#####################################################################


# Current problem: Only consider bottom have object to be blocks
# If object goes over midpoint and has 4 verts, it must be center or corner post *******


import cv2
import numpy as np
import imutils
import sys
import json
import time
import serial
import RPi.GPIO as GPIO

from picamera.array import PiRGBArray
from picamera import PiCamera


# Sets up serial
serialPath = "/dev/ttyACM" + sys.argv[1]
g_SER=serial.Serial(serialPath,9600)  # Change ACM number as found from ls /dev/tty/ACM*
g_SER.baudrate=9600


# Creates the vars to avoid error in functions
hsv = 0
frame = 0
mask = 0
frameWidth = 600
frameHeight = 500

# Starts the camera feed, starts output feed
camera = cv2.VideoCapture(0)
# outputVideo = cv2.VideoWriter('output.avi',cv2.VideoWriter_fourcc('D','I','V','X'), 20.0, (int(camera.get(3)),int(camera.get(4))))

# Gets base color from command line, else uses hardcoded
if (len(sys.argv) == 4):
    baseColor = (int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
else:
    baseColor = (67, 125, 90)


g_lowerColorRange = (0,0,0)
g_upperColorRange = (0,0,0)
percentDifference = 0.4

# Sets up color ranges based on base given color
g_lowerColorRange = (baseColor[0] - baseColor[0]*percentDifference, baseColor[1] - baseColor[1]*percentDifference, baseColor[2] - baseColor[2]*percentDifference)
g_upperColorRange = (baseColor[0] + baseColor[0]*percentDifference, baseColor[1] + baseColor[1]*percentDifference, baseColor[2] + baseColor[2]*percentDifference)



# Loads all 4 colors from JSON file
def getColorsFromJSON(fileLocation):
    loadedColors = []
    with open(fileLocation, 'r') as f:
        loadedColors = json.loads(f.readline().rstrip('\n'))
    colors = []

    #Adds lower up upper bounds
    for color in loadedColors:
        temp = {}
        temp['lower'] = (color[0] - color[0]*percentDifference, color[1] - color[1]*percentDifference, color[2] - color[2]*percentDifference)
        temp['upper'] = (color[0] + color[0]*percentDifference, color[1] + color[1]*percentDifference, color[2] + color[2]*percentDifference)
        colors.append(temp)

    return colors


# Updates the color & upper color ranges when clicking on hsv
def updateColorRangeWhenClick(event, x, y, flags, param):
    global g_lowerColorRange, g_upperColorRange, percentDifference
    # If it wasn't a left click, then break here
    if event != cv2.EVENT_LBUTTONDOWN:
        return

    color = hsv[y, x]
    g_lowerColorRange = (color[0] - color[0]*percentDifference, color[1] - color[1]*percentDifference, color[2] - color[2]*percentDifference)
    g_upperColorRange = (color[0] + color[0]*percentDifference, color[1] + color[1]*percentDifference, color[2] + color[2]*percentDifference)
    print("Color: ", color)

# Returns the center of object and the enclosing circle x, y and radius of object
def getObjectSpecs(largestContour):

    ((x, y), radius) = cv2.minEnclosingCircle(largestContour)
    M = cv2.moments(largestContour)
    center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

    # Ignores object if shape is above halfway point
    if (center[1] > frameHeight*.33):
        return None


    # approxShape = detectShape(largestContour)
    # print("Approx Shape: " + approxShape)
    return {"center" : center, "x" : x, "y" : y,"radius" : radius}


# Loops through all contours and labels/outlines the shapes
def identifyAndLabelAllShapes(mask, frame):
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = cnts[0] if imutils.is_cv2() else cnts[1]

    largestContour = None
    largestArea = 0

    # Sorts contours by size
    sortedContours = sorted(contours, key=lambda x: cv2.contourArea(x))
    sortedContours.reverse()

    # Loops through first 8 contours (largest ones, avoids small annoying artifacts)
    for contour in sortedContours[:8]:
        try:
            ((x, y), radius) = cv2.minEnclosingCircle(contour)
            M = cv2.moments(contour)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            
            # Only uses object if below halfway
            if (center[1] > frameHeight*.33):
                approxShape, aspectRatio = detectShape(contour)
                area = cv2.contourArea(contour)
                specs = {"center" : center, "x" : x, "y" : y,"radius" : radius, "shape" : approxShape}

                # If area of object is less than amount, ignore it, probably an artifcat
                if (area < 75):
                    continue

                
                cv2.putText(frame, specs["shape"], (int(specs["x"])+ int(specs["radius"]), int(specs["y"])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                cv2.putText(frame, str(area)[:5], (int(specs["x"])+ int(specs["radius"]), int(specs["y"])+ 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)                
                # cv2.putText(frame, str(aspectRatio)[:5], (int(specs["x"])+ int(specs["radius"]), int(specs["y"])+ 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                cv2.drawContours(frame, [contour], -1, (255,255,255), 2)

                # Calculates area of contour and saves if largest and block/circle
                if (area > largestArea and (approxShape == "Block" or approxShape == "Circle")):
                    largestArea = area
                    largestContour = contour
                
        except:
            None

    return (largestContour, largestArea)

# Detects the shape of the contour
def detectShape(contour):
    # Source: https://www.pyimagesearch.com/2016/02/08/opencv-shape-detection/
    # initialize the shape name and approximate the contour
    shape = "unidentified"
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.04 * peri, True)
    aspectRatio = 0
    
    ((x, y), radius) = cv2.minEnclosingCircle(contour)
    M = cv2.moments(contour)
    center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
    (x, y, w, h) = cv2.boundingRect(approx)
    area = cv2.contourArea(contour)

    # if the shape is a triangle, it will have 3 vertices
    if len(approx) == 3:
        shape = "triangle"

    # if the shape has 4 vertices, it is either a square or
    # a rectangle
    elif len(approx) == 4:
        # compute the bounding box of the contour and use the
        # bounding box to compute the aspect ratio
        (x, y, w, h) = cv2.boundingRect(approx)
        aspectRatio = w / float(h)

        # a square will have an aspect ratio that is approximately
        # equal to one, otherwise, the shape is a rectangle
        if aspectRatio < 0.4:
            shape = "Corner Post"
        # elif aspectRatio >= 0.35 and aspectRatio <= 0.85 and center[0]+h/2 < frameHeight/2 or area > 10000:
        elif area > 10000:
            shape = "Center Post"
        elif aspectRatio > 0.40:    #Was 0.6
            shape = "Block"


    # otherwise, we assume the shape is a circle
    else:
        # if (center[0]+h/2 < frameHeight/2 or area > 10000):
        if (area > 10000):
            shape = "Center Post"
        else:
            shape = "Circle"

    # return the name of the shape
    return shape, aspectRatio

# Reads from serial, returns the text
def readFromSerial():
	dataReceived = g_SER.readline()
	return dataReceived

# Writes data to serial
def writeToSerial(dataToSend):
    # If input is 'quit', it closes the connection
	if (dataToSend == 'quit'):
		closeSerialConnection()
		return

	if (dataToSend[-1] != '@'):
		dataToSend = dataToSend + '@'

	# Writes to serial
	g_SER.write(dataToSend)

# Closes the serial communication
def closeSerialConnection():
    g_SER.close()

# Writes to arduino and waits for a response
def writeAndReadToSerial(dataToSend):
    writeToSerial(dataToSend)
    dataReceived = readFromSerial()
    return dataReceived

# Names the windows
# cv2.namedWindow("mask")
cv2.namedWindow("frame")
# cv2.namedWindow("hsv")
# cv2.setMouseCallback("frame", updateColorRangeWhenClick)

# Current area of screen of object being tracked
currentPosition = None

# colorSavedFile = 'RaspberryPiCode/OpenCV/colorCalibration.json'
colorSavedFile = 'colorCalibration.json'
colors = getColorsFromJSON(colorSavedFile)


# Starts the camera feed
camera = PiCamera()
camera.resolution = (frameWidth, frameWidth)
camera.framerate = 32
rawCapture = PiRGBArray(camera)

# allow the camera to warmup
time.sleep(1)


for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    startTime = time.time()
    frame = frame.array

    
    # Resize frame so it can be processed quicker
    # frame = imutils.resize(frame, height=frameHeight)
    frame = cv2.resize(frame,(frameWidth, frameHeight))


    # Blur to reduce extra noise
    blurStart = time.time()
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    print("Blue time:", time.time()-blurStart)

    # Convert to HSV colorspace
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    largestContourAndArea = (0,0)

    # Gets the places in image between the color two bounds
        # Then removes any extra small blobs
    masks = []
    for color in colors:
        mask = cv2.inRange(hsv, color['lower'], color['upper'])
        masks.append(mask)

    # Combines all masks 
    mask = cv2.bitwise_or(masks[0], masks[1])
    mask = cv2.bitwise_or(mask, masks[2])
    mask = cv2.bitwise_or(mask, masks[3])

    largestContourAndArea = identifyAndLabelAllShapes(mask, frame)
    objectSpecs = getObjectSpecs(largestContourAndArea[0])

    
    # # Outlines largest contour that is a shape or ball
    if (largestContourAndArea[1] != 0):
        cv2.drawContours(frame, [largestContourAndArea[0]], -1, (0,0,0), 2)

    # cv2.imshow('hsv', hsv)
    cv2.imshow('frame', frame)
    # cv2.imshow('mask', mask)

    # Closes when pressing 's'
    if cv2.waitKey(1) & 0xFF == ord('s'):
        cv2.imwrite( "finalImage.jpg", frame)
        break

    # TODO - Change to make it only print if the position changes from left/right/center
        # - Maybe store variable with current left/right/center

    if (objectSpecs != None):
        # Tells if object is left, right, or center of screen
        if ((int(objectSpecs["x"]) - int(objectSpecs["radius"])) <= frameWidth/2 and (int(objectSpecs["x"]) + int(objectSpecs["radius"])) >= frameWidth/2):
            if (currentPosition != "center"):
                currentPosition = "center"
                print("Its in the center")
                received = writeAndReadToSerial("GO forward 80@")
        elif ((int(objectSpecs["x"]) - int(objectSpecs["radius"])) <= frameWidth/2 and (int(objectSpecs["x"]) + int(objectSpecs["radius"])) <= frameWidth/2):
            if (currentPosition != "left"):
                currentPosition = "left"
                print("Its on the left")
                received = writeAndReadToSerial("GO right 25@")
        elif ((int(objectSpecs["x"]) - int(objectSpecs["radius"])) >= frameWidth/2 and (int(objectSpecs["x"]) + int(objectSpecs["radius"])) >= frameWidth/2):
            if (currentPosition != "right"):
                currentPosition = "right"
                print("Its on the right")
                received = writeAndReadToSerial("GO left 25@") 
    else:
        print("No object detected")

    totalTime = time.time() - startTime
    # outputVideo.write(frame)
    rawCapture.truncate(0)


    print("Frame time: ", totalTime)


# Closes all windows opened
camera.release()
# outputVideo.release()
#camera.destroyAllWindows()