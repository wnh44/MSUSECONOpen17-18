# Following tutorials from:
#
# https://pythonprogramming.net/loading-images-python-opencv-tutorial/

from __future__ import print_function
import cv2
import numpy as np
from matplotlib import pyplot as plt
import argparse
import time


#---------THRESHOLDING AND PASTING LOGO-------
def logopaste():
    img1 = cv2.imread('3D-Matplotlib.png')
    img2 = cv2.imread('mainlogo.png')

    rows, cols, channels = img2.shape
    roi = img1[0:rows, 0:cols]

    img2gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    ret, mask = cv2.threshold(img2gray, 220, 255, cv2.THRESH_BINARY_INV)
    mask_inv = cv2.bitwise_not(mask)

    img1_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)

    img2_fg = cv2.bitwise_and(img2, img2, mask=mask)

    dst = cv2.add(img1_bg, img2_fg)
    img1[0:rows, 0:cols] = dst

    #                    (img1, weight, img2, weight, gamma)
    add = cv2.addWeighted(img1, 0.6, img2, 0.4, 0)

#-------BASIC IMAGE MANIPULATION--------
def pixelselection():
    img = cv2.imread('watch.jpg', 1)
    img[100:150, 100:150] = [255, 255, 255]
    px = img[100:150, 100:150]
    print(img.shape)
    print(img.size)
    print(img.dtype)
    watch_face = img[37:111, 107:194]
    img[0:74, 0:87] = watch_face

#-------SHAPES------------------------
def drawshapes():

    img = cv2.imread('watch.jpg', 1)
        # (img, start, end, color(bgr), thickness)
    cv2.line(img,(0, 150), (150,150), (255, 255, 255), 15)
    cv2.rectangle(img, (15, 25), (290, 150), (0, 0, 255), 2)
    cv2.circle(img, (100, 63), 55, (0, 255, 0), 2)
    pts = np.array([[10, 5], [20,30], [70,20], [50,10]], np.int32)
    cv2.polylines(img, [pts], True, (0, 255, 255), 1)

    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, 'OpenCV Tuts!', (0, 130), font, 1, (200, 255, 155), 2, cv2.LINE_AA)

# #----COMPLEX THRESHOLDING----------
def thresholding():

    img = cv2.imread('bookpage.jpg')
    grayscaled = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    th = cv2.adaptiveThreshold(grayscaled, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 115, 1)
    retval, threshold = cv2.threshold(grayscaled, 10, 255, cv2.THRESH_BINARY)


    cv2.imshow('original', img)
    cv2.imshow('Adaptive threshold', th)

#--------VIDEO CAPTURE AND BLURRING-----------------------
def captureblur():
    cap = cv2.VideoCapture(0)

    while(1):
        _, frame = cap.read()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower_red = np.array([30, 150, 50])
        upper_red = np.array([255, 255, 180])

        mask = cv2.inRange(hsv, lower_red, upper_red)
        res = cv2.bitwise_and(frame, frame, mask=mask)

        kernel = np.ones((15,15), np.float32)/225
        smoothed = cv2.filter2D(res, -1, kernel)
        blur = cv2.GaussianBlur(res, (15,15), 0)
        median = cv2.medianBlur(res, 15)
        bilateral = cv2.bilateralFilter(res, 15, 75, 75)

        cv2.imshow('bilateral Blur', bilateral)
        # cv2.imshow('Median Blur', median)
        # cv2.imshow('Gaussian Blurring', blur)
        # cv2.imshow('Original', frame)
        # cv2.imshow('Averaging', smoothed)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
    cap.release()

#--------MORPHOLOGICAL TRANSFORM-------------------
def morph():
    cap = cv2.VideoCapture(0)
    counter = 0

    while(1):
        _, frame = cap.read()
        if counter == 0:
            img_name = "opencv_frame_{}.png".format(0)
            cv2.imwrite(img_name, frame)
            counter += 1
        cv2.circle(frame, (100, 63), 30, (0, 0, 255), -1)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_red = np.array([30, 150, 50])
        upper_red = np.array([255, 255, 180])
        # lower_red = np.array([13, 127, 153])
        # upper_red = np.array([328, 255, 180])
        lower_yellow = np.array([30, 150, 50])
        upper_yellow = np.array([255, 255, 180])
        lower_blue = np.array([30, 150, 50])
        upper_blue = np.array([255, 255, 180])
        lower_green = np.array([30, 150, 50])
        upper_green = np.array([255, 255, 180])

        redmask = cv2.inRange(hsv, lower_red, upper_red)
        yellowmask = cv2.inRange(hsv, lower_yellow, upper_yellow)
        bluemask = cv2.inRange(hsv, lower_blue, upper_blue)
        greenmask = cv2.inRange(hsv, lower_green, upper_green)

        # res = cv2.bitwise_and(frame, frame, mask=mask)

        # kernel = np.ones((5,5),np.uint8)

        # erosion = cv2.erode(mask, kernel, iterations = 1)
        # dilation = cv2.dilate(mask, kernel, iterations = 1)
        # opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        # closing = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        # tophat = cv2.morphologyEx(mask, cv2.MORPH_TOPHAT, kernel)
        # blackhat = cv2.morphologyEx(mask, cv2.MORPH_BLACKHAT, kernel)



        cv2.imshow('hsv', hsv)
        cv2.imshow('redmask', redmask)
        # cv2.imshow('yellowmask', yellowmask)
        # cv2.imshow('bluemask', bluemask)
        # cv2.imshow('greenmask', greenmask)
        # cv2.imshow('erosion', erosion)
        # cv2.imshow('dilation', dilation)
        # cv2.imshow('opening', opening)
        # cv2.imshow('closing', closing)
        # cv2.imshow('tophat', tophat)
        # cv2.imshow('blackhat', blackhat)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
    cap.release()

#--------EDGE DETECTION-----------------------
def edgedetect():
    cap = cv2.VideoCapture(0)

    while(1):
        _, frame = cap.read()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower_red = np.array([30, 150, 50])
        upper_red = np.array([255, 255, 180])

        mask = cv2.inRange(hsv, lower_red, upper_red)
        res = cv2.bitwise_and(frame, frame, mask=mask)

        laplacian = cv2.Laplacian(frame, cv2.CV_64F)
        sobelx = cv2.Sobel(frame, cv2.CV_64F, 1, 0, ksize=5)
        sobely = cv2.Sobel(frame, cv2.CV_64F, 0, 1, ksize=5)

        cv2.imshow('original', frame)
        # cv2.imshow('mask', mask)
        # cv2.imshow('laplacian', laplacian)
        # cv2.imshow('sobelx', sobelx)
        # cv2.imshow('sobely', sobely)
        edges = cv2.Canny(frame, 100, 200)
        cv2.imshow('edges', edges)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
    cap.release()

#--------TEMPLATE MATCHING------------------
def templatematch():
    img_rgb = cv2.imread('ghostpatch.jpg')
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

    template = cv2.imread('ghostpatch.jpg', 0)
    template = template[204:257,59:92]
    w, h = template.shape[::-1]

    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where(res >= threshold)

    for pt in zip(*loc[::-1]):
        cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 255, 255), 2)

    #cv2.imshow('detected', img_rgb)
    cv2.imshow('rgb', img_rgb)
    cv2.imshow('template', template)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

#-------FOREGROUND EXTRACTION----------------
def foregroundextract():
    img = cv2.imread('bread.jpg', 1)
    height, width, depth = img.shape
    imgScale = 500/height
    newX, newY = img.shape[1]*imgScale, img.shape[0]*imgScale
    img = cv2.resize(img, (int(newX), int(newY)))
    mask = np.zeros(img.shape[:2], np.uint8)

    bgdModel = np.zeros((1,65),np.float64)
    fgdModel = np.zeros((1,65),np.float64)

    rect = (281, 153, 144, 347)

    cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
    mask2 = np.where((mask==2) | (mask==0), 0, 1).astype('uint8')
    img = img*mask2[:,:,np.newaxis]

    plt.imshow(img)
    plt.colorbar()
    plt.show()

    # cv2.imshow('img', img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

#------CORNER DETECTION--------------------

# All this stuff is for the range sliders and stuff///////////////////////////////////////////
max_value = 255
max_value_h = 360 // 2
low_h = 0
low_s = 0
low_v = 0
high_h = max_value_h
high_s = max_value
high_v = max_value
capture = 'Video Capture'
detect = 'Object Detection'
low_h_name = 'Low H'
low_s_name = 'Low S'
low_v_name = 'Low V'
high_h_name = 'High H'
high_s_name = 'High S'
high_v_name = 'High V'

def on_low_h_thresh_trackbar(val):
    global low_h
    global high_h
    low_h = val
    low_h = min(high_h-1, low_h)
    cv2.setTrackbarPos(low_h_name, detect, low_h)

def on_high_h_thresh_trackbar(val):
    global low_h
    global high_h
    high_h = val
    high_h = max(high_h, low_h+1)
    cv2.setTrackbarPos(high_h_name, detect, high_h)

def on_low_s_thresh_trackbar(val):
    global low_s
    global high_s
    low_s = val
    low_s = min(high_s-1, low_s)
    cv2.setTrackbarPos(low_s_name, detect, low_s)

def on_high_s_thresh_trackbar(val):
    global low_s
    global high_s
    high_s = val
    high_s = max(high_s, low_s+1)
    cv2.setTrackbarPos(high_s_name, detect, high_s)

def on_low_v_thresh_trackbar(val):
    global low_v
    global high_v
    low_v = val
    low_v = min(high_v-1, low_v)
    cv2.setTrackbarPos(low_v_name, detect, low_v)

def on_high_v_thresh_trackbar(val):
    global low_v
    global high_v
    high_v = val
    high_v = max(high_v, low_v+1)
    cv2.setTrackbarPos(high_v_name, detect, high_v)

parser = argparse.ArgumentParser(description='Code for Thresholding Operations using inRange tutorial.')
parser.add_argument('--camera', help='Camera divide number.', default=0, type=int)
args = parser.parse_args()

cap = cv2.VideoCapture(0)

cv2.namedWindow(capture)
cv2.namedWindow(detect)

cv2.createTrackbar(low_h_name, detect, low_h, max_value_h, on_low_h_thresh_trackbar)
cv2.createTrackbar(high_h_name, detect, high_h, max_value_h, on_high_h_thresh_trackbar)
cv2.createTrackbar(low_s_name, detect, low_s, max_value, on_low_s_thresh_trackbar)
cv2.createTrackbar(high_s_name, detect, high_s, max_value, on_high_s_thresh_trackbar)
cv2.createTrackbar(low_v_name, detect, low_v, max_value, on_low_v_thresh_trackbar)
cv2.createTrackbar(high_v_name, detect, high_v, max_value, on_high_v_thresh_trackbar)


while True:

    ret, frame = cap.read()
    frame = cv2.resize(frame, (600, 500))
    if frame is None:
        break
    frame_HSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # frame_threshold = cv2.inRange(frame_HSV, (low_h, low_s, low_v), (high_h, high_s, high_v))

    # I tested with the frame threshold to get these ranges for the colors
    blue = cv2.inRange(frame_HSV, (105, 190, 0), (120,255,180))
    green = cv2.inRange(frame_HSV, (50, 95, 60), (85,255,180))
    yellow = cv2.inRange(frame_HSV, (10, 85, 0), (45,255,180))

    # Since the red ball and the red paint are on different ends of the hue spectrum
    # I had to add the two masks for those ranges
    redball = cv2.inRange(frame_HSV, (0, 130, 0), (10,255,180))
    redeverything = cv2.inRange(frame_HSV, (130, 160, 0), (180, 255, 255))
    red = cv2.add(redball, redeverything)

    cv2.imshow(capture, frame)
    # cv2.imshow('hsv', frame_HSV)
    # cv2.imshow(detect, frame_threshold)
    cv2.imshow('blue', blue)
    cv2.imshow('green', green)
    # cv2.imshow('redball', redball)
    # cv2.imshow('redeverything', redeverything)
    cv2.imshow('red', red)
    cv2.imshow('yellow', yellow)


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
cap.release()