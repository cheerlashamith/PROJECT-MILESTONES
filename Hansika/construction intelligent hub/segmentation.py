import cv2
import numpy as np


# ---------------------------------------
# Detect Building Wall Region
# ---------------------------------------

def detect_wall(image):

    img = image.copy()

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Ignore blue sky
    lower_blue = np.array([90, 40, 40])
    upper_blue = np.array([140,255,255])

    sky = cv2.inRange(hsv, lower_blue, upper_blue)

    # Ignore green trees
    lower_green = np.array([35,40,40])
    upper_green = np.array([90,255,255])

    trees = cv2.inRange(hsv, lower_green, upper_green)

    # Everything except sky & trees
    mask = cv2.bitwise_not(sky | trees)

    kernel = np.ones((7,7),np.uint8)

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        kernel
    )

    mask = cv2.GaussianBlur(mask,(11,11),0)

    return mask