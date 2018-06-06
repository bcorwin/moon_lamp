#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 31 14:57:08 2018

@author: Ben Corwin
"""

import urllib
import json
import datetime
import csv

def usno_oneday(date, loc):
  """
  Source: http://aa.usno.navy.mil/data/docs/api.php#rstt
  """
  url = "http://api.usno.navy.mil/rstt/oneday?date=" + urllib.parse.quote(date)
  url += "&loc=" + urllib.parse.quote(loc)
  
  req = urllib.request.Request(url)
  r = urllib.request.urlopen(req).read()
  results = json.loads(r.decode('utf-8'))
  
  return(results)
  
def secondary_phase_selector(usno_phase, fracillum):
  """
  Takes a secondry phase and fracillum and converts it to a phase number (0-11)
  """
  secondary_phases = {
  'Waxing Crescent': [1,2,   0.0, 0.5],
  'Waxing Gibbous' : [4,5,   0.5, 1.0],
  'Waning Gibbous' : [7,8,   1.0, 0.5],
  'Waning Crescent': [10,11, 0.5, 0.0]}  
  
  min_phase, max_phase, min_frac, max_frac = secondary_phases[usno_phase]
  if abs(fracillum - min_frac) <= abs(fracillum - max_frac):
    return(min_phase)
  else:
    return(max_phase)

def process_phase(usno_data):
  """
  Takes data from USNO and converts the phase and fracillum to a phase number.
  A phase number is 0 - 11 (since the lamp can display 12 phases)
  """
  if 'curphase' in usno_data:
    usno_phase = usno_data['curphase']
  else:
    usno_phase = usno_data['closestphase']['phase']

  if 'fracillum' in usno_data:
    fracillum = usno_data['fracillum'].replace('%', '')
    fracillum = float(fracillum)/100
    phase_num = secondary_phase_selector(usno_phase, fracillum)
  else:
    primary_fracillum = {
    'New Moon'     : [0.0, 0],
    'First Quarter': [0.5, 3],
    'Full Moon'    : [1.0, 6],
    'Last Quarter' : [0.5, 9]}
    fracillum, phase_num = primary_fracillum[usno_phase]
  
  out = [usno_phase, fracillum, phase_num]
  return(out)
  
def create_output(start, end, loc):
  """
  Writes a csv file with date, phase number, fracillum, phase name, and moon rise
  """
  out = []
  start_date = datetime.datetime.strptime(start, "%m/%d/%Y")
  end_date   = datetime.datetime.strptime(end, "%m/%d/%Y")
  step       = datetime.timedelta(days=1)
  while start_date <= end_date:
    curdate = start_date.date().strftime("%m/%d/%Y")
    usno_data = usno_oneday(curdate, loc)
    usno_phase, fracillum, phase_num = process_phase(usno_data)
    out += [[curdate, usno_phase, fracillum, phase_num, loc]]
    start_date += step
  with open("../configs/moon_info.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerows(out)

start_date = datetime.date.today()
end_date = start_date + datetime.timedelta(days=30)

start_date = start_date.strftime("%m/%d/%Y")
end_date = end_date.strftime("%m/%d/%Y")

create_output(start_date, end_date, "Chicago, IL")