import asyncio
import websockets
from PIL import Image
import json
import cv2
import numpy as np
import base64
from io import BytesIO
from lane_line_detection import calculate_control_signal

async def echo(websocket, path):
    async for message in websocket:
        # Get image from simulation
        data = json.loads(message)
        image = Image.open(BytesIO(base64.b64decode(data["image"])))
        image = np.asarray(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        #
        # # Prepare visualization image
        draw = image.copy()
        #
        # # Send back throttle and steering angle
        throttle, steering_angle = calculate_control_signal(image, draw=draw)
        # throttle, steering_angle = 0.5, -0.5
        #
        # # Show the result to a window
        # draw = cv2.cvtColor(draw, cv2.COLOR_BGR2HSV)
        # # lower mask (0-10)
        # lower_white = np.array([0,0,100], dtype=np.uint8)
        # upper_white = np.array([0,0,255], dtype=np.uint8)
        #
        # # Threshold the HSV image to get only white colors
        # mask = cv2.inRange(draw, lower_white, upper_white)
        cv2.imshow("Result", draw)
        cv2.waitKey(1)

        # Send back throttle and steering angle
        message = json.dumps({"throttle": throttle, "steering": steering_angle})
        print(message)
        await websocket.send(message)


async def main():
    async with websockets.serve(echo, "0.0.0.0", 4567, ping_interval=None):
        await asyncio.Future()  # run forever

asyncio.run(main())
