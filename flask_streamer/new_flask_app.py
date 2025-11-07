# USAGE
# python webstreaming.py --ip 0.0.0.0

# import the necessary packages

import threading
import argparse
import datetime
import time
import imutils
import cv2
import adafruit_dht
import board
import socket
from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template
from adafruit_servokit import ServoKit

sensor = adafruit_dht.DHT11(board.D18)

kit = ServoKit(channels=16)
pan = 0
tilt = 1
kit.servo[pan].set_pulse_width_range(700, 2300)
kit.servo[tilt].set_pulse_width_range(700, 2000)
panValue = 90
tiltValue = 90
tiltMin = 0
tiltMax = 160
panMin = 0
panMax = 180
increment = 10
# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful for multiple browsers/tabs
# are viewing tthe stream)
OUT_FRAME = None
LOCK = threading.Lock()

FPS_TEXT = 0
WEATHER_TEXT = ''
# initialize a flask object
app = Flask(__name__)

# initialize the video stream and allow the camera sensor to
# warmup
VS = VideoStream(usePiCamera=1, framerate=24, resolution=(640, 480))
VS.start()
#vs = VideoStream(src=0).start()
time.sleep(2.0)


@app.route("/")
def index():
        # return the rendered template
        return render_template("new_index.html")

def update_frame():
        # grab global references to the video stream, output frame, and
        # lock variables
        global VS, OUT_FRAME, LOCK, FPS_TEXT

        start_time = datetime.datetime.now()
        frameCount = 0
        # loop over frames from the video stream
        while True:
                # read the next frame from the video stream, resize it,
                frame = VS.read()
                frame = imutils.resize(frame, width=640)
                frame = imutils.rotate(frame, 180)
                #frameCount += 1
                #fps = frameCount / ((datetime.datetime.now() - start_time).total_seconds())

                #cv2.putText(frame, str(round(fps, 2)), (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
                #cv2.putText(frame, str(round(FPS_TEXT, 2)), (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
                cv2.putText(frame, WEATHER_TEXT, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                #cv2.putText(frame, str(frameCount), (10, frame.shape[0] - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

                # acquire the lock, set the output frame, and release the
                # lock
                with LOCK:
                        OUT_FRAME = frame.copy()

def move_servos(panMove, tiltMove):
    global panMax, panMin, tiltMin, tiltMax, pan, tilt, tiltValue, panValue

    panValue = max(panMin, min(panMax, panMove))
    tiltValue = max(tiltMin, min(tiltMax, tiltMove))

    kit.servo[pan].angle = panValue
    kit.servo[tilt].angle = tiltValue

@app.route("/box")
def box():
    move_servos(90, 80)
    return ('', 200)

@app.route("/door")
def door():
    global tiltMin

    move_servos(90, tiltMin)
    return ('', 200)

@app.route("/perch")
def perch():
    global tiltMax

    move_servos(90, tiltMax)
    return ('', 200)

@app.route("/up")
def up():
    global panValue, tiltValue, increment

    move_servos(panValue, tiltValue+increment)
    return ('', 200)

@app.route("/down")
def down():
    global panValue, tiltValue, increment

    move_servos(panValue, tiltValue-increment)
    return ('', 200)

@app.route("/right")
def right():
    global panValue, tiltValue, increment

    move_servos(panValue+increment, tiltValue)
    return ('', 200)

@app.route("/left")
def left():
    global panValue, tiltValue, increment

    move_servos(panValue-increment, tiltValue)
    return ('', 200)

def weather():
        global WEATHER_TEXT, sensor
        while True:
                try:
                        humidity = sensor.humidity
                        temperature = sensor.temperature

                        if humidity is not None and temperature is not None:
                                temperature = temperature * 9/5 + 32
                                WEATHER_TEXT = '{}F'.format(temperature) + ' - {}%'.format(humidity)
                except:
                        pass

                time.sleep(2.0)

def generate():
        # grab global references to the output frame and lock variables
        global OUT_FRAME, LOCK, FPS_TEXT

        start_time = datetime.datetime.now()
        count = 0
        # loop over frames from the output stream
        while True:
                # wait until the lock is acquired
                with LOCK:
                        time = datetime.datetime.now()
                        # check if the output frame is available, otherwise skip
                        # the iteration of the loop
                        if OUT_FRAME is None:
                                continue

                        # encode the frame in JPEG format
                        (flag, encodedImage) = cv2.imencode(".jpg", OUT_FRAME)
                        count += 1
                        FPS_TEXT = count / ((datetime.datetime.now() - start_time).total_seconds())
                        # ensure the frame was successfully encoded
                        if not flag:
                                continue

                        OUT_FRAME = None
                        #delay = int((0.3 - (datetime.datetime.now() - time).total_seconds())* 1000)
                        #print(delay)
                        cv2.waitKey(1)
                # yield the output frame in the byte format
                yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
                        bytearray(encodedImage) + b'\r\n')

@app.route("/video_feed")
def video_feed():
        # return the response generated along with the specific media
        # type (mime type)
        return Response(generate(),
                mimetype = "multipart/x-mixed-replace; boundary=frame")

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

# check to see if this is the main thread of execution
if __name__ == '__main__':
        # Find the IP to host from
        ip = get_ip()

        # start a thread that will perform motion detection
        t = threading.Thread(target=update_frame)
        t.daemon = True
        t.start()

        w = threading.Thread(target=weather)
        w.daemon = True
        w.start()

        # start the flask app
        app.run(host=ip, port=8000, debug=True,
                threaded=True, use_reloader=False)

# release the video stream pointer
VS.stop()
