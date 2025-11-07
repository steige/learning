# Servo Control
from time import sleep
#from gpiozero import AngularServo
from adafruit_servokit import ServoKit
kit = ServoKit(channels=16)

max = 180
kit.servo[1].actuation_range = max

kit.servo[1].set_pulse_width_range(700, 1850)
up = True
value = 0
while True:
    kit.servo[1].angle = value
    sleep(.2)
    if up:
        value += 5
        if value == max:
            up = False
    else:
        value -= 5
        if value == 0:
            up = True


