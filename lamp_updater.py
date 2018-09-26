#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 14:11:32 2018

@author: ben.corwin
"""
import config
import json
import csv
import datetime

MOON_INFO_FILE = config.FILE_PATHS['moon_info']
MOON_TIMES_FILE = config.FILE_PATHS['moon_times_file']

with open(config.FILE_PATHS['moon_lamp'], 'r') as f:
  data = json.load(f)
  phase_mode = data['phase']['mode']
  phase_phase = data['phase']['phase']
  lamp_mode = data['lamp']['mode']

CURRENT_INFO = None
with open(MOON_INFO_FILE, 'r') as f:
  reader = csv.reader(f)
  for row in reader:
    if(row[0] == datetime.datetime.today().strftime('%m/%d/%Y')):
      CURRENT_INFO = row
      break

CURRENT_PHEN = None
current_dt = datetime.datetime.utcnow()
with open(MOON_TIMES_FILE, 'r') as f:
  reader = csv.reader(f)
  prev_phen, prev_time = None, None
  for row in reader:
    phen, time = row
    time = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
    
    if prev_time is not None and current_dt > prev_time and current_dt <= time:
      CURRENT_PHEN = prev_phen
      break
    
    prev_phen, prev_time = phen, time

    
def get_current_phase():
  """
  Reads the moon lamp config file and returns the current phase number
  """
  if CURRENT_INFO != None:
    return(CURRENT_INFO[3])
  else:
    return(-1)

def get_phase_num(phase_mode):
  out = -1
  phase_mode = phase_mode.lower()
  if phase_mode == 'current':
    out = get_current_phase()
  return(out)

# Update pin_status in lights.json
if phase_mode == 'current':
  phase_num = get_current_phase()
  pin_status = config.LAMP_PHASES[phase_num]
elif phase_mode == 'hold':
  phase_num = config.PHASE_NAMES[phase_phase]
  pin_status = config.LAMP_PHASES[phase_num]
else:
  # ERROR: phase_mode not defined
  pin_status = ['on', 'off', 'on', 'off', 'on', 'off']

# Update lamp status in lights.json
if lamp_mode == 'on':
  light_on = True
elif lamp_mode == 'off':
  light_on = False
elif lamp_mode == 'with_moon':
  light_on = False if CURRENT_PHEN == 'S' else True
  if CURRENT_PHEN not in ['S', 'R']:
    # ERROR: moon_times not available
    pin_status = ['off', 'off', 'on', 'on', 'off', 'off']  
else:
  # ERROR: lamp_mode not defined
  pin_status = ['off', 'on', 'off', 'on', 'off', 'on'] 
  light_on = True
  
lights_data = {"pin_status": pin_status, "on": light_on, "cur_phase": phase_num}

print(lights_data)

with open(config.FILE_PATHS['lights'], 'w') as outfile:
    json.dump(lights_data, outfile)
  