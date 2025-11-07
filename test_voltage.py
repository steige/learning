import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(23,GPIO.OUT)

print "Turning on"
GPIO.output(23,GPIO.HIGH)

try:
  while True:
    print "Testing..."
finally:
  GPIO.cleanup()

