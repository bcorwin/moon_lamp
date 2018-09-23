#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import config

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

PINS = config.MOON_LAMP_CONFIG['pins']

# Set mode and turn all on
for pinNum in PINS:
  GPIO.setup(pinNum,GPIO.OUT)
  GPIO.output(pinNum,GPIO.HIGH)

time.sleep(3)

# All off
for pinNum in PINS:
  GPIO.output(pinNum,GPIO.LOW)

time.sleep(3)

# One at a time in order
for pinNum in PINS:
  GPIO.output(pinNum,GPIO.HIGH)
  time.sleep(1)
  GPIO.output(pinNum,GPIO.LOW)
  time.sleep(1)
