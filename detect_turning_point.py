import cv2

def detect_turning_point(img, draw=None):
    im_height, im_width = img.shape[:2]
    center = im_height // 2
    center_width = im_width // 2
    left_vertical_line_x = int(75) 
    right_vertical_line_x = int(im_width-75) 
    bottom_vertical_y = center + 230
    top_vertical_y = center 
    horizon_y = im_height - 1
    distance_between_center_and_horizon_line = 60
    horizon_line_width = 250
    horizon_line_left_start = center_width - distance_between_center_and_horizon_line - horizon_line_width
    horizon_line_left_end = horizon_line_left_start + horizon_line_width
    horizon_line_right_start = center_width + distance_between_center_and_horizon_line 
    horizon_line_right_end = horizon_line_right_start + horizon_line_width

    if draw is not None:
        cv2.line(draw, (left_vertical_line_x, top_vertical_y),
                 (left_vertical_line_x, bottom_vertical_y), (0, 0, 255), 2)
        cv2.line(draw, (right_vertical_line_x, top_vertical_y),
                 (right_vertical_line_x, bottom_vertical_y), (0, 0, 255), 2)
        cv2.line(draw, (horizon_line_left_start, horizon_y),
                 (horizon_line_left_end, horizon_y), (0, 0, 255), 2)
        cv2.line(draw, (horizon_line_right_start, horizon_y),
                 (horizon_line_right_end, horizon_y), (0, 0, 255), 2)

    left_vertical_line = img[ : ,left_vertical_line_x]
    right_vertical_line = img[ : ,right_vertical_line_x]
    horizon_line = img[horizon_y, :]

    top_left_turning_point = -1
    top_right_turning_point = -1
    bottom_left_turning_point = -1
    bottom_right_turning_point = -1

    for x in range(top_vertical_y, bottom_vertical_y):
        if left_vertical_line[x] > 50:
            top_left_turning_point = x
            break
    for x in range(top_vertical_y, bottom_vertical_y):
        if right_vertical_line[x] > 50:
            top_right_turning_point = x
            break
    for x in range(horizon_line_left_start, horizon_line_left_end):
        if horizon_line[x] > 50:
            bottom_left_turning_point = x
            break
    for x in range(horizon_line_right_start, horizon_line_right_end):
        if horizon_line[x] > 50:
            bottom_right_turning_point = x
            break

    if draw is not None:
        if top_left_turning_point != -1:
            draw = cv2.circle(
                draw, (left_vertical_line_x, top_left_turning_point), 7, (255, 255, 0), -1)
        if top_right_turning_point != -1:
            draw = cv2.circle(
                draw, (right_vertical_line_x, top_right_turning_point), 7, (255, 255, 0), -1)
        if bottom_left_turning_point != -1:
            draw = cv2.circle(
                draw, (bottom_left_turning_point, horizon_y), 7, (255, 255, 0), -1)
        # if bottom_right_turning_point != -1:
            draw = cv2.circle(
                draw, (bottom_right_turning_point, horizon_y), 7, (255, 255, 0), -1)

    # cv2.imshow("Traffic signs", draw)
    # cv2.waitKey(1)

    return bottom_left_turning_point == -1, bottom_right_turning_point == -1
    # return top_left_turning_point != -1 and bottom_left_turning_point == -1, bottom_right_turning_point == -1 and top_right_turning_point != -1
    # return top_left_turning_point != -1,  top_right_turning_point != -1
