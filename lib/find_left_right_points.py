import cv2
from lib.detect_turning_point import detect_turning_point
from parameter import LANE_WIDTH, POSTION_WHEN_TURN

def find_left_right_points(image, turn, draw=None):
    """Find left and right points of lane
    """

    im_height, im_width = image.shape[:2]

    # Consider the position 70% from the top of the image
    # interested_line_y = int(im_height * 0.9)
    # interested_line_y = int(im_height*0.97)
    # higher_line_y = int(im_height*0.85)
    interested_line_y = int(im_height*0.9)
    # higher_line_y = int(im_height*0.65)
    if draw is not None:
        cv2.line(draw, (0, interested_line_y),
                 (im_width, interested_line_y), (0, 0, 255), 2)
        # cv2.line(draw, (0, higher_line_y),
        #          (im_width, higher_line_y), (0, 0, 255), 2)
    # higher_line = image[higher_line_y, :]
    interested_line = image[interested_line_y, :]

    # higher_left_point = -1
    # higher_right_point = -1
    # higher_center_point = -1
    # Detect left/right points
    left_point = -1
    right_point = -1
    center = im_width // 2
    # cv2.line(draw, (center, 0),
    #          (center, im_height), (0, 0, 255), 2)

    # for x in range(2, im_width):
    #     if higher_line[x] > 100:
    #         higher_left_point = x
    #         break
    # for x in range(im_width - 1, 2, -1):
    #     if higher_line[x] > 100:
    #         higher_right_point = x
    #         break

    # if higher_left_point == -1 and higher_right_point == -1:
    #     higher_left_point = 0
    #     higher_right_point = im_width - 1

    # if higher_left_point != -1 and higher_right_point != -1:
    #     higher_center_point = (higher_right_point + higher_left_point) // 2

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
    
    if right_point - left_point < 30:
        if left_point > center: 
            left_point = right_point - LANE_WIDTH
        if  left_point < center: 
            right_point = left_point + LANE_WIDTH


    left_turn, right_turn = detect_turning_point(image, draw=draw)

    # print(left_turn, right_turn)
    # print(turn)

    if left_turn and turn == "left":
        left_point = 0
        right_point = left_point + 10
    if right_turn and turn == "right":
        right_point = im_width
        left_point = right_point - 10
    if right_turn and turn == "no_left":
        right_point = im_width
        left_point = right_point - 10
    if left_turn and turn == "no_right":
        left_point = 0
        right_point = left_point + 10
    

    if draw is not None:
        if left_point != -1:
            draw = cv2.circle(
                draw, (left_point, interested_line_y), 7, (255, 255, 0), -1)
        if right_point != -1:
            draw = cv2.circle(
                draw, (right_point, interested_line_y), 7, (0, 255, 0), -1)
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
