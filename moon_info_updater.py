#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 31 14:57:08 2018

@author: Ben Corwin

To do: track rising and set times (in UTC) so lamp mode with_moon works
To do: track phase start/end times (in UTC) so lamp mode with_change works
To do: don't store date because that could get messed up in tz conversion
Use the tz parameter from the returned data to convert times to UTC.
^ Also need to use isdst to adjust
"""

import config
import urllib.parse
import urllib.request
import json
import datetime
import csv
import re

OUT_FILE = config.FILE_PATHS['moon_info']
MOON_TIMES_FILE = config.FILE_PATHS['moon_times_file']

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
  
def process_times(usno_data):
  pull_year  = usno_data['year']
  pull_mon   = usno_data['month']
  pull_day   = usno_data['day']
  gmt_offset = usno_data['tz']
  isdst      = usno_data['isdst'] == 'yes'
  prevmoondata = usno_data.get('prevmoondata')
  prevmoondata = prevmoondata if prevmoondata is not None else []

  prev_date = datetime.date(pull_year, pull_mon, pull_day) - datetime.timedelta(days=1)

  if isdst:
    gmt_offset += 1
  
  moon_times = []

  for i in prevmoondata:
    phen = i['phen']
    if phen not in ["R", "S"]: continue
    time = re.sub('([ap])\.(m)\..*', '\g<1>\g<2>', i['time']).upper()
    time = datetime.datetime.strptime(time, '%I:%M %p')
    time = datetime.datetime(prev_date.year, prev_date.month, prev_date.day, time.hour, time.minute)
    time -= datetime.timedelta(hours=gmt_offset)
    moon_times += [[phen, time]]
      

  for i in usno_data['moondata']:
    phen = i['phen']
    if phen not in ["R", "S"]: continue
    time = re.sub('([ap])\.(m)\..*', '\g<1>\g<2>', i['time']).upper()
    time = datetime.datetime.strptime(time, '%I:%M %p')
    time = datetime.datetime(pull_year, pull_mon, pull_day, time.hour, time.minute)
    time -= datetime.timedelta(hours=gmt_offset)
    moon_times += [[phen, time]]

  return(moon_times)
  
def clean_moon_times(moon_times):
  """
  Removes duplicate times and sorts the data by the utc datetime
  """
  out = []
  times = []
  for i in moon_times:
    phen, time = i
    if time not in times:
      times += [time]
      out += [[phen, time]]

  out = sorted(out, key=lambda x: x[1])
  return(out)
  
def create_outputs(start, end, loc):
  """
  Writes two csv files
    1) date, phase number, fracillum, phase name, and moon rise
    2) phen (Rise or Set) and UTC datetime of event
  """
  moon_phases = []
  moon_times  = []

  start_date = datetime.datetime.strptime(start, "%m/%d/%Y")
  end_date   = datetime.datetime.strptime(end, "%m/%d/%Y")
  step       = datetime.timedelta(days=1)
  
  while start_date <= end_date:
    curdate = start_date.date().strftime("%m/%d/%Y")
    print("Pulling moon info for", curdate)
    usno_data = usno_oneday(curdate, loc)
    usno_phase, fracillum, phase_num = process_phase(usno_data)
    moon_times += process_times(usno_data)
    moon_phases += [[curdate, usno_phase, fracillum, phase_num, loc]]
    start_date += step

  moon_times = clean_moon_times(moon_times)
  
  with open(MOON_TIMES_FILE, "w") as f:
    writer = csv.writer(f)
    writer.writerows(moon_times)
  with open(OUT_FILE, "w") as f:
    writer = csv.writer(f)
    writer.writerows(moon_phases)

start_date = datetime.date.today()
end_date = start_date + datetime.timedelta(days=30)

start_date = start_date.strftime("%m/%d/%Y")
end_date = end_date.strftime("%m/%d/%Y")

create_outputs(start_date, end_date, "Chicago, IL")
