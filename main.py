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
from traffic_sign_detection import detect_traffic_signs
from lane_line_detection import calculate_control_signal

# Initialize traffic sign classifier
traffic_sign_model = cv2.dnn.readNetFromONNX("traffic_sign_classifier_lenet_v3.onnx")

g_image_queue = Queue(maxsize=5)
traffic_sign_queue = Queue(maxsize=5)  # New queue for traffic sign messages
stop = False

def process_traffic_sign_loop(image_queue, sign_queue):
    while True:
        if image_queue.empty():
            time.sleep(0.1)
            continue
        image = image_queue.get()
        # Prepare visualization image
        draw = image.copy()
        # Detect traffic signs
        detected_signs = detect_traffic_signs(image, traffic_sign_model, draw=draw)
        # Show the result to a window
        cv2.imshow("Traffic signs", draw)
        cv2.waitKey(1)
        # If a stop sign is detected, send a message to the main process
        for sign in detected_signs:
            if sign[0] == "stop":
                if not sign_queue.full():
                    sign_queue.put("stop")

def controller(image, draw):
    global stop

    throttle, steering_angle = calculate_control_signal(image, draw=draw)

    if stop:
        return -2, steering_angle
    
    if traffic_sign_queue.empty():
        return throttle, steering_angle

    match traffic_sign_queue.get():
        case "stop":
            stop = True
            throttle = -1

    return throttle, steering_angle

async def process_image(websocket, path):
    async for message in websocket:
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
        print(message)
        await websocket.send(message)


async def main():
    async def handler(websocket, path):
        await process_image(websocket, path)

    async with websockets.serve(handler, "0.0.0.0", 4567, ping_interval=None):
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    p = Process(target=process_traffic_sign_loop, args=(g_image_queue, traffic_sign_queue))
    p.start()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        p.terminate()
        p.join()
