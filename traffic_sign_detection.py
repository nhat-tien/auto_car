import cv2
import numpy as np

def filter_signs_by_color(image):
    """Filter all objects with red or blue color - traffic sign candidate
    """
    # Convert image to HSV color space
    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Filter red. There are two ranges of red color
    lower1, upper1 = np.array([0, 70, 50]), np.array([10, 255, 255])
    lower2, upper2 = np.array([170, 70, 50]), np.array([180, 255, 255])
    mask_1 = cv2.inRange(image_hsv, lower1, upper1)
    mask_2 = cv2.inRange(image_hsv, lower2, upper2)
    mask_r = cv2.bitwise_or(mask_1, mask_2)

    # Filter blue color
    lower3, upper3 = np.array([100, 150, 0]), np.array([140, 255, 255])
    mask_b = cv2.inRange(image_hsv, lower3, upper3)

    # Combine the result
    mask_final = cv2.bitwise_or(mask_r, mask_b)
    return mask_final

def get_boxes_from_mask(mask):
    """Find bounding boxes from color
    """
    bboxes = []

    nccomps = cv2.connectedComponentsWithStats(mask, 4, cv2.CV_32S)
    numLabels, labels, stats, centroids = nccomps
    im_height, im_width = mask.shape[:2]
    for i in range(1, numLabels):  # Start from 1 to skip background
        x = stats[i, cv2.CC_STAT_LEFT]
        y = stats[i, cv2.CC_STAT_TOP]
        w = stats[i, cv2.CC_STAT_WIDTH]
        h = stats[i, cv2.CC_STAT_HEIGHT]
        area = stats[i, cv2.CC_STAT_AREA]
        # Filter small objects
        if w < 20 or h < 20:
            continue
        # Filter too large objects
        if w > 0.8 * im_width or h > 0.8 * im_height:
            continue
        # Remove objects with too different width/height ratio
        if w / h > 2.0 or h / w > 2.0:
            continue
        bboxes.append([x, y, w, h])
    return bboxes

def detect_traffic_signs(img, model, draw=None):
    """Detect traffic signs on an image
    """
    # Traffic sign classes. unknown means "not a traffic sign"
    classes = ['unknown', 'left', 'no_left', 'right',
               'no_right', 'straight', 'stop']

    # Detect traffic signs by color
    mask = filter_signs_by_color(img)
    bboxes = get_boxes_from_mask(mask)

    # Preprocess
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_rgb = img_rgb.astype(np.float32)
    img_rgb = img_rgb / 255.0

    # Classify signs using CNN
    signs = []
    for bbox in bboxes:
        # Crop sign area
        x, y, w, h = bbox
        sub_image = img_rgb[y:y+h, x:x+w]

        if sub_image.shape[0] < 20 or sub_image.shape[1] < 20:
            continue

        # Preprocess
        sub_image_resized = cv2.resize(sub_image, (32, 32))
        sub_image_expanded = np.expand_dims(sub_image_resized, axis=0)

        # Use CNN to get prediction
        model.setInput(sub_image_expanded)
        preds = model.forward()
        preds = preds[0]
        cls = preds.argmax()
        score = preds[cls]

        # Remove unknown objects
        if cls == 0:
            continue

        # Remove low confidence objects
        if score < 0.5:
            continue

        sign = classes[cls]
        signs.append([classes[cls], x, y, w, h])

        # Draw prediction result
        if draw is not None:
            text = f"{classes[cls]} {score:.2f}"
            cv2.rectangle(draw, (x, y), (x+w, y+h), (0, 255, 255), 2)
            cv2.putText(draw, text, (x, y-5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    return signs
