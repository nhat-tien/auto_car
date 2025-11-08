import websockets
import asyncio
import time
from PIL import Image
import json
import cv2
import numpy as np
import base64
from io import BytesIO
from multiprocessing import Queue, Process
from lib.find_boundary_lanes import  highlight_gray_area
from lib.traffic_sign_detection import detect_traffic_signs
from controller import calculate_control_signal
from lib.pid import PID 
from parameter import KP, KI, KD, THROTTLE_WHEN_SEE_SIGN, TIME_KEEP_SIGN, THROTTLE

# Initialize traffic sign classifier
traffic_sign_model = cv2.dnn.readNetFromONNX("traffic_sign_classifier_lenet_v3.onnx")


g_image_queue = Queue(maxsize=5)
traffic_sign_queue = Queue(maxsize=5)  # New queue for traffic sign messages
stop = False
turn = None
timer = 0
pid = PID(KP, KI, KD, setpoint=0)

def process_traffic_sign_loop(image_queue, sign_queue):
    global timer
    while True:
        if image_queue.empty():
            time.sleep(0.1)
            continue
        image = image_queue.get()
        im_height, im_width = image.shape[:2]
        # y = 0
        # x = 100
        # image = image[y:im_height,x:x+800]
        # Prepare visualization image
        draw = image.copy()
        # Detect traffic signs
        detected_signs = detect_traffic_signs(image, traffic_sign_model, draw=draw)
        # Show the result to a window
        cv2.imshow("Traffic signs", draw)
        cv2.waitKey(1)
        # If a stop sign is detected, send a message to the main process
        # if detected_signs == []:
        #     sign_queue.put("none")
        # else:
        #     for sign in detected_signs:
        #         if sign[0]:
        #             sign_queue.put(sign[0])
        #         # if not sign_queue.full():
        if detected_signs == []: 
            if timer == 0:
                sign_queue.put("none")
            else: 
                timer -= 1
        else:
            for sign in detected_signs:
                sign_queue.put(sign[0])
                timer = TIME_KEEP_SIGN
        # for sign in detected_signs:
        #     if sign[0]:
        #         sign_queue.put(sign[0])


def controller(image, draw):
    global stop
    global pid
    global turn

    throttle, steering_angle = calculate_control_signal(image, pid, turn, draw=draw)

    # if stop:
    #     return -10, steering_angle
 
    if not traffic_sign_queue.empty():
        sign = traffic_sign_queue.get()
        # print(sign)
        match sign:
            # case "stop":
            #     stop = True
            #     throttle = -1
            case "no_left":
                turn = "no_left"
                throttle = THROTTLE_WHEN_SEE_SIGN 
            case "no_right":
                turn = "no_right"
                throttle = THROTTLE_WHEN_SEE_SIGN
            case "straight":
                turn = "straight"
            case "left":
                turn = "left"
                throttle = THROTTLE_WHEN_SEE_SIGN
            case "right":
                turn = "right"
                throttle = THROTTLE_WHEN_SEE_SIGN
            case "none":
                turn = "none"
                throttle = THROTTLE


    return throttle, steering_angle

async def process_image(conn):
    async for message in conn:
        # Get image from simulation
        data = json.loads(message)
        image = Image.open(BytesIO(base64.b64decode(data["image"])))
        image = np.asarray(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        g_image_queue.put(image)
        #
        # # Prepare visualization image
        draw = image.copy()
        #
        # # Send back throttle and steering angle
        throttle, steering_angle = controller(image, draw) 

        cv2.imshow("Result", draw)
        cv2.waitKey(1)

        # Send back throttle and steering angle
        message = json.dumps({"throttle": throttle, "steering": steering_angle})
        # print(message)
        await conn.send(message)


async def main():
    async def handler(websocket):
        await process_image(websocket)

    async with websockets.serve(handler, "0.0.0.0", 4567, ping_interval=None):
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    p = Process(target=process_traffic_sign_loop, args=(g_image_queue, traffic_sign_queue))
    # p = Process(target=test_find_boundary_lanes, args=(g_image_queue, traffic_sign_queue))
    p.start()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        p.terminate()
        p.join()
