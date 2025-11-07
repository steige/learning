#from picamera.array import PiRGBArray
#from picamera import PiCamera
import cv2
#import RPi.GPIO as GPIO
import time
import Adafruit_DHT
import imutils
from imutils.video import VideoStream
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

sensor = Adafruit_DHT.DHT11
sensorpin = 14

vs = VideoStream(usePiCamera=1).start()
time.sleep(2.0)

humidity, temperature = "", ""

try:
  while True:
    # grab the raw NumPy array representing the image, then initialize the $
    # and occupied/unoccupied text
    ##humidity, temperature = Adafruit_DHT.read_retry(sensor, sensorpin)
    ##if humidity is not None and temperature is not None:
       ## temperature = temperature * 9/5.0 + 32
        ##text = '{}F'.format(temperature) + '{}%'.format(humidity)
    kit.servo[pan].angle = panValue
    kit.servo[tilt].angle = tiltValue

    frame = vs.read()
    #frame = imutils.resize(frame, width=680)

    cv2.putText(frame, 'Test', (10, frame.shape[0] - 10),cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

    # show the frame
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    # clear the stream in preparation for the next frame

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
      break
    if key == ord("a"):
        if panValue < panMax:
            panValue += incriment
    if key == ord("d"):
        if panValue > panMin:
            panValue -= incriment
    if key == ord("w"):
        if tiltValue > tiltMin:
            tiltValue -= incriment
    if key == ord("s"):
        if tiltValue < tiltMax:
            tiltValue += incriment

    print (panValue, tiltValue)

finally:
    pass
