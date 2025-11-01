import cv2
import numpy as np

def find_boundary_lines(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower_green = np.array([35, 50, 50], dtype=np.uint8)
    upper_green = np.array([85, 255, 255], dtype=np.uint8)

    lower_gray = np.array([0, 0, 40], dtype=np.uint8)
    upper_gray = np.array([180, 60, 255], dtype=np.uint8)

    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    mask_gray  = cv2.inRange(hsv, lower_gray, upper_gray)

    kernel = np.ones((3,3), np.uint8)
    green_d = cv2.dilate(mask_green, kernel, 1)

    boundary = cv2.bitwise_and(green_d, mask_gray)

    boundary = cv2.Canny(boundary, 20, 80)

    return boundary
