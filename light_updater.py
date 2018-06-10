#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun June 10 14:08:08 2018

@author: Ben Corwin
"""

import config
import json
import RPi.GPIO as GPIO

LIGHT_FILE = config.FILE_PATHS['lights']
PINS = config.MOON_LAMP_CONFIG['pins']

GPIO.setmode(GPIO.BCM)

def switch_led(pinNum, status):
  GPIO.setup(pinNum,GPIO.OUT)
  if status.lower() == "on":
    GPIO.output(pinNum,GPIO.HIGH)
    print(pinNum, "set to on")
  else:
    GPIO.output(pinNum,GPIO.LOW)
    print(pinNum, "set to off")
  GPIO.cleanup(pinNum)

with open(LIGHT_FILE) as f:
  data = json.load(f)
  lights_status = data['pin_status']
  lights_on = data['on']

if lights_on == True:
  for idx, pin in enumerate(PINS):
    status = lights_status[idx]
    switch_led(pin, status)
else:
  for pin in PINS:
    switch_led(pin, "off")
