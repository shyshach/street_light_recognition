import cv2
import numpy as np  
import imutils
from collections import deque

def color_threshold_hsv(image):
    
        lower_yellow = np.array([0, 0, 0])
        upper_yellow = np.array([60, 255, 255])

        pts = deque(maxlen=64)

        vs = image

        font = cv2.FONT_HERSHEY_SIMPLEX
        #print(vs.shape)
        frame1 = imutils.resize(vs, width=400)
        frame = imutils.resize(vs, width=400)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        mask1 = cv2.inRange(hsv, lower_yellow, upper_yellow)
        mask =  mask1
        mask = cv2.GaussianBlur(mask, (1, 1), 0)

        output_img = frame1.copy()
        output_img[np.where(mask!=255)] = 0
        
        cv2.imwrite('masked_image.jpg',output_img)
    
        return output_img

def process(image):
    img = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    lab_planes = cv2.split(img)
    original = lab_planes[0]

    adjusted = adjust_gamma(original, 0.5)
    adjusted = np.float32(adjusted)
    return adjusted

def adjust_gamma(image, gamma):
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
        for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(image, table)

def cal_luminosity(image):

    image = process(image)
    x,y = image.shape

    val=0
    for i in range(0,x):
        for j in range(0,y):
            val = val + image[i][j]

    avg_val = val/(x*y)
    return avg_val

# img= cv2.imread('static/uploads/pred_st8_st1.png')
# print(cal_luminosity(img))