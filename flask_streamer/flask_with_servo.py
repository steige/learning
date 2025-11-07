
# USAGE
# python webstreaming.py --ip 0.0.0.0

# import the necessary packages
from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template
from flask import request
import threading
import argparse
import datetime
import imutils
import time
import cv2
import Adafruit_DHT
import http
from adafruit_servokit import ServoKit

kit = ServoKit(channels=16)
pan = 0
tilt = 1
kit.servo[pan].set_pulse_width_range(700, 2300)
kit.servo[tilt].set_pulse_width_range(700, 2000)
panValue = 90
tiltValue = 90
incriment = 5
tiltMin = 0
tiltMax = 160
panMin = 0
panMax = 180

kit.servo[pan].angle = panValue
kit.servo[tilt].angle = tiltValue

# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful for multiple browsers/tabs
# are viewing tthe stream)
outputFrame = None
lock = threading.Lock()

sensor = Adafruit_DHT.DHT11
text = ""
publishrate = 0

app = Flask(__name__)

# initialize the video stream and allow the camera sensor to
# warmup
vs = VideoStream(usePiCamera=1).start()
#vs = VideoStream(src=0).start()
time.sleep(2.0)

def weather():
        global text, sensor
        while True:
                humidity, temperature = Adafruit_DHT.read_retry(sensor, 18)
                if humidity is not None and temperature is not None:
                        temperature = temperature * 9/5.0 + 32
                        text = '{}F'.format(temperature) + ' - {}%'.format(humidity)

def move_servo(xmove, ymove):
    global kit, panValue, tiltValue

    panValue = min(panMax,max((panValue + int(int(xmove)) / 5),panMin))
    tiltValue = min(tiltMax,max((tiltValue + int(int(ymove)) / 5),tiltMin))

    kit.servo[pan].angle = panValue
    kit.servo[tilt].angle = tiltValue

@app.route('/move', methods=['GET'])
def update_servo():
    xmove =  request.args.get('xmove', None)
    ymove =  request.args.get('ymove', None)
    print(xmove, ymove)
    move_servo(xmove, ymove)
    return ('', 200)

@app.route("/door")
def door():
    global kit, panMin, panMax, tiltMin, tiltmax

    kit.servo[pan].angle = 90
    kit.servo[tilt].angle = 80
    return ('', 200)

@app.route("/box")
def box():
    global kit, panMin, panMax, tiltMin, tiltmax

    kit.servo[pan].angle = 80
    kit.servo[tilt].angle = tiltMin
    return ('', 200)

@app.route("/")
def index():
        # return the rendered template
        print("this")
        return render_template("new_index.html")

def detect_motion():
        # grab global references to the video stream, output frame, and
        # lock variables
        global vs, outputFrame, lock, text, publishrate
        framecount = 0
        starttime = datetime.datetime.now()
        # loop over frames from the video stream
        while True:
                # read the next frame from the video stream, resize it,
                # convert the frame to grayscale, and blur it
                frame = vs.read()
                frame = imutils.resize(frame, width=400)
                framecount += 1
                fps = framecount / (datetime.datetime.now() - starttime).total_seconds()

                cv2.putText(frame, text, (10, frame.shape[0] - 10),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(frame, str(round(fps,2)), (10, frame.shape[0] - 30),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(frame, str(round(publishrate,2)), (10, frame.shape[0] - 60),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                # acquire the lock, set the output frame, and release the
                # lock
                with lock:
                        outputFrame = frame.copy()
def generate():
        # grab global references to the output frame and lock variables
        global outputFrame, lock, publishrate

        counter = 0
        starttime = datetime.datetime.now()
        # loop over frames from the output stream
        while True:
                # wait until the lock is acquired
                with lock:
                        # check if the output frame is available, otherwise skip
                        # the iteration of the loop
                        if outputFrame is None:
                                continue

                        counter += 1
                        publishrate = counter / (datetime.datetime.now() - starttime).total_seconds()

                        # encode the frame in JPEG format
                        (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)

                        # ensure the frame was successfully encoded
                        if not flag:
                                continue

                        outputFrame = None

                # yield the output frame in the byte format
                yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
                        bytearray(encodedImage) + b'\r\n')

@app.route("/video_feed")
def video_feed():
        # return the response generated along with the specific media
        # type (mime type)
        return Response(generate(),
                mimetype = "multipart/x-mixed-replace; boundary=frame")

# check to see if this is the main thread of execution
if __name__ == '__main__':
        # construct the argument parser and parse command line arguments
        ap = argparse.ArgumentParser()
        ap.add_argument("-i", "--ip", type=str, default='192.168.0.101',
                help="ip address of the device")
        args = vars(ap.parse_args())

        # start a thread that will perform motion detection
        t = threading.Thread(target=detect_motion)
        t.daemon = True
        t.start()

        threading.Thread(target=weather).start()

        # start the flask app
        app.run(host=args["ip"], port=8000, debug=True,
                threaded=True, use_reloader=False)

# release the video stream pointer
vs.stop()

