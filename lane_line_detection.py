import cv2
import numpy as np
import json
from calculate_control_signal import calculate_angle
from find_left_right_points import find_left_right_points
from parameter import ANGLE_CONTROL_ENABLE, MAX_ERROR_TO_FULL_ANGLE, LANE_WIDTH, THROTTLE, POSTION_WHEN_TURN

# KP = 0.0411
# KI = 0.001
# KD = 0.0152

# Good 
# KP = 0.6
# KI = 0.01
# KD = 0.7

# KP = 0.9
# KI = 1
# KD = 1


def find_lane_lines(img):
    """
    Detecting road markings
    This function will take a color image, in BGR color system,
    Returns a filtered image of road markings
    """

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_white = np.array([0,0,10], dtype=np.uint8)
    upper_white = np.array([0,0,255], dtype=np.uint8)

    mask = cv2.inRange(hsv, lower_white, upper_white)

    return mask 

def birdview_transform(img):
    """Apply bird-view transform to the image
    """
    IMAGE_H = 480
    IMAGE_W = 640
    src = np.float32([[0, IMAGE_H], [640, IMAGE_H], [0, IMAGE_H * 0.4], [IMAGE_W, IMAGE_H * 0.4]])
    dst = np.float32([[240, IMAGE_H], [640 - 240, IMAGE_H], [-160, 0], [IMAGE_W+160, 0]])
    M = cv2.getPerspectiveTransform(src, dst) # The transformation matrix
    warped_img = cv2.warpPerspective(img, M, (IMAGE_W, IMAGE_H)) # Image warping
    return warped_img

def calculate_control_signal(img, pid, turn, draw=None):
    """Calculate speed and steering angle
    """

    # Find left/right points
    img_lines = find_lane_lines(img)
    # img_birdview = birdview_transform(img_lines)
    # draw[:, :] = birdview_transform(draw)
    # new_draw = birdview_transform(draw.copy())
    # image = birdview_transform(img_lines)
    left_point, right_point = find_left_right_points(img_lines, turn, draw=draw)

    # Calculate speed and steering angle
    # The speed is fixed to 50% of the max speed
    # You can try to calculate speed from turning angle
    throttle = THROTTLE
    steering_angle = 0
    im_center = img.shape[1] // 2

    if left_point != -1 and right_point != -1:

        # Calculate the deviation
        center_point = (right_point + left_point) // 2
        center_diff =  im_center - center_point

        # Calculate steering angle
        # You can apply some advanced control algorithm here
        # For examples, PID
        steering_angle = calculate_angle(pid(center_diff), ANGLE_CONTROL_ENABLE, MAX_ERROR_TO_FULL_ANGLE)

    return throttle, steering_angle

