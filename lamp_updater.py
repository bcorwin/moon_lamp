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

chk = get_phase_num(phase_mode)
print(chk)
