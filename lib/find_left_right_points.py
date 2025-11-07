import cv2
from lib.detect_turning_point import detect_turning_point
from parameter import LANE_WIDTH, POSTION_WHEN_TURN, THROTTLE

def find_left_right_points(image, turn, draw=None):
    """Find left and right points of lane
    """

    im_height, im_width = image.shape[:2]

    interested_line_y = int(im_height*0.9)

    if draw is not None:
        cv2.line(draw, (0, interested_line_y),
                 (im_width, interested_line_y), (0, 0, 255), 2)
    interested_line = image[interested_line_y, :]

    left_point = -1
    right_point = -1
    center = im_width // 2

    for x in range(0, im_width):
        if interested_line[x] > 100:
            left_point = x
            break
    for x in range(im_width - 1, 0, -1):
        if interested_line[x] > 100:
            right_point = x
            break

    if left_point == -1 and right_point == -1:
        left_point = 0
        right_point = im_width-1

    if turn != "straight":
        if right_point - left_point > LANE_WIDTH:
            if left_point < int(center*0.25): 
                left_point = right_point - LANE_WIDTH
            if  right_point > int(center*1.75): 
                right_point = left_point + LANE_WIDTH



    left_turn, right_turn = detect_turning_point(image, draw=draw)
    # left_turn = False
    # right_turn = False
    # if left_point < center*0.25:
    #     left_turn = True
    # if right_point > center*1.75:
    #     right_turn = True


    the_width_of_turn = 300

    if left_turn and turn == "left":
        left_point = 0
        right_point = left_point + the_width_of_turn
    if right_turn and turn == "right":
        right_point = im_width
        left_point = right_point - the_width_of_turn
    if right_turn and turn == "no_left":
        right_point = im_width
        left_point = right_point - the_width_of_turn
    if left_turn and turn == "no_right":
        left_point = 0
        right_point = left_point + the_width_of_turn
    

    if draw is not None:
        if left_point != -1:
            draw = cv2.circle(
                draw, (left_point, interested_line_y), 7, (255, 255, 0), -1)
        if right_point != -1:
            draw = cv2.circle(
                draw, (int(right_point), interested_line_y), 7, (0, 255, 0), -1)
        # if higher_right_point != -1:
        #     draw = cv2.circle(
        #         draw, (higher_right_point, higher_line_y), 7, (0, 255, 0), -1)
        # if higher_left_point != -1:
        #     draw = cv2.circle(
        #         draw, (higher_left_point, higher_line_y), 7, (255, 255, 0), -1)
        # if higher_center_point != -1:
        #     draw = cv2.circle(
        #         draw, (higher_center_point, higher_line_y), 7, (0, 255, 255), -1)


    return left_point, right_point 
