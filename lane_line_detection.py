import cv2
import numpy as np
from pid import PID 
import json


def find_lane_lines(img):
    """
    Detecting road markings
    This function will take a color image, in BGR color system,
    Returns a filtered image of road markings
    """

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_white = np.array([0,0,70], dtype=np.uint8)
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


def find_left_right_points(image, draw=None):
    """Find left and right points of lane
    """

    im_height, im_width = image.shape[:2]

    # Consider the position 70% from the top of the image
    # interested_line_y = int(im_height * 0.9)
    interested_line_y = im_height-1
    higher_line_y = int(im_height*0.85)
    if draw is not None:
        cv2.line(draw, (0, interested_line_y),
                 (im_width, interested_line_y), (0, 0, 255), 2)
        cv2.line(draw, (0, higher_line_y),
                 (im_width, higher_line_y), (0, 0, 255), 2)
    higher_line = image[higher_line_y, :]
    interested_line = image[interested_line_y, :]

    higher_left_point = -1
    higher_right_point = -1
    higher_center_point = -1
    # Detect left/right points
    left_point = -1
    right_point = -1
    lane_width = 150
    center = im_width // 2
    cv2.line(draw, (center, 0),
             (center, im_height), (0, 0, 255), 2)

    for x in range(0, im_width):
        if higher_line[x] > 0:
            higher_left_point = x
            break
    for x in range(im_width - 1, 0, -1):
        if higher_line[x] > 0:
            higher_right_point = x
            break

    if higher_left_point != -1 and higher_right_point != -1:
        higher_center_point = (higher_right_point + higher_left_point) // 2

    for x in range(0, im_width):
        if interested_line[x] > 0:
            left_point = x
            break
    for x in range(im_width - 1, 0, -1):
        if interested_line[x] > 0:
            right_point = x
            break

    if right_point - left_point < 30:
        if left_point > higher_center_point: 
            left_point = right_point - lane_width
        if  left_point < higher_center_point: 
            right_point = left_point + lane_width

    # Predict right point when only see the left point
    # if left_point != -1 and right_point == -1:
    #     right_point = left_point + lane_width
    #
    # # Predict left point when only see the right point
    # if right_point != -1 and left_point == -1:
    #     left_point = right_point - lane_width

    # Draw two points on the image
    if draw is not None:
        if left_point != -1:
            draw = cv2.circle(
                draw, (left_point, interested_line_y), 7, (255, 255, 0), -1)
        if right_point != -1:
            draw = cv2.circle(
                draw, (right_point, interested_line_y), 7, (0, 255, 0), -1)
        if higher_right_point != -1:
            draw = cv2.circle(
                draw, (higher_right_point, higher_line_y), 7, (0, 255, 0), -1)
        if higher_left_point != -1:
            draw = cv2.circle(
                draw, (higher_left_point, higher_line_y), 7, (255, 255, 0), -1)
        if higher_center_point != -1:
            draw = cv2.circle(
                draw, (higher_center_point, higher_line_y), 7, (0, 255, 255), -1)

    return left_point, right_point

def calculate_angle(num):
    max = 20
    if num < -max or num > max:
        return 1 if num > 0 else -1
    else:
        return (1/max)*num

pid = PID(1.0, 0, 0, setpoint=0)

def calculate_control_signal(img, draw=None):
    """Calculate speed and steering angle
    """

    # Find left/right points
    img_lines = find_lane_lines(img)
    img_birdview = birdview_transform(img_lines)
    draw[:, :] = birdview_transform(draw)
    left_point, right_point = find_left_right_points(img_birdview, draw=draw)

    # Calculate speed and steering angle
    # The speed is fixed to 50% of the max speed
    # You can try to calculate speed from turning angle
    throttle = 0.5
    steering_angle = 0
    im_center = img.shape[1] // 2

    if left_point != -1 and right_point != -1:

        # Calculate the deviation
        center_point = (right_point + left_point) // 2
        center_diff =  im_center - center_point

        # Calculate steering angle
        # You can apply some advanced control algorithm here
        # For examples, PID
        steering_angle = calculate_angle(pid(center_diff))

    return throttle, steering_angle

