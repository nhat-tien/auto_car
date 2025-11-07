import cv2
from lib.find_boundary_lanes import highlight_gray_area
import numpy as np
import json
from lib.find_left_right_points import find_left_right_points
from lib.calculate_angle import calculate_angle
from parameter import (
    ANGLE_CONTROL_ENABLE,
    MAX_ERROR_TO_FULL_ANGLE,
    LANE_WIDTH,
    THROTTLE,
    POSTION_WHEN_TURN,
)


def find_lane_lines(img):

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_white = np.array([0,0,5], dtype=np.uint8)
    upper_white = np.array([0,0,255], dtype=np.uint8)

    mask = cv2.inRange(hsv, lower_white, upper_white)

    return mask 

def calculate_control_signal(img, pid, turn, draw=None):
    """Calculate speed and steering angle
    """
    print(turn)

    # Find left/right points
    # img_lines = find_lane_lines(img)
    img_lines = highlight_gray_area(img)
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

