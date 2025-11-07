import cv2

def detect_turning_point(img, draw=None):
    im_height, im_width = img.shape[:2]
    center = im_height // 2
    center_width = im_width // 2
    horizon_y = int(im_height-1)
    distance_between_center_and_horizon_line = 60
    horizon_line_width = 20
    horizon_line_left_start = 0
    horizon_line_left_end = horizon_line_width
    horizon_line_right_start = im_width - 1
    horizon_line_right_end = horizon_line_right_start - horizon_line_width

    if draw is not None:
        cv2.line(draw, (horizon_line_left_start, horizon_y),
                 (horizon_line_left_end, horizon_y), (0, 0, 255), 2)
        cv2.line(draw, (horizon_line_right_start, horizon_y),
                 (horizon_line_right_end, horizon_y), (0, 0, 255), 2)

    horizon_line = img[horizon_y, :]

    bottom_left_turning_point = -1
    bottom_right_turning_point = -1

    for x in range(horizon_line_left_start, horizon_line_left_end):
        if horizon_line[x] > 100:
            bottom_left_turning_point = x
            break
    for x in range(horizon_line_right_start, horizon_line_right_end, -1):
        if horizon_line[x] > 100:
            bottom_right_turning_point = x
            break

    if draw is not None:
        if bottom_left_turning_point != -1:
            draw = cv2.circle(
                draw, (bottom_left_turning_point, horizon_y), 7, (255, 255, 0), -1)
        if bottom_right_turning_point != -1:
            draw = cv2.circle(
                draw, (bottom_right_turning_point, horizon_y), 7, (255, 255, 0), -1)

    # cv2.imshow("Traffic signs", draw)
    # cv2.waitKey(1)

    return bottom_left_turning_point != -1, bottom_right_turning_point != -1
