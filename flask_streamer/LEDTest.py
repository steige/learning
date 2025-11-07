import RPi.GPIO as gpio
import time

gpio.setmode(gpio.BCM)
gpio.setup(21, gpio.IN)
gpio.setup(18, gpio.OUT)

light = True

while True:
    x = gpio.input(21)
    print(x)
    if x == 1:
        light = not light
        
    if light:
        gpio.output(18, gpio.HIGH)
    else:
        gpio.output(18, gpio.LOW)
    
    time.sleep(1)

gpio.cleanup()