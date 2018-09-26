MOON_LAMP_CONFIG = {
  'pins': [2, 3, 4, 17, 27, 22]
}

FILE_PATHS = {
  'moon_info': 'configs/moon_info.csv',
  'lights': 'configs/lights.json',
  'moon_lamp': 'configs/moon_lamp.json',
  'moon_times_file': 'configs/moon_times.csv'
}

LAMP_PHASES = {
  '0': ['off', 'off', 'off', 'off', 'off', 'off'],
  '1': ['off', 'off', 'off', 'off', 'off', 'on'],
  '2': ['off', 'off', 'off', 'off', 'on', 'on'],
  '3': ['off', 'off', 'off', 'on', 'on', 'on'],
  '4': ['off', 'off', 'on', 'on', 'on', 'on'],
  '5': ['off', 'on', 'on', 'on', 'on', 'on'],
  '6': ['on', 'on', 'on', 'on', 'on', 'on'],
  '7': ['on', 'on', 'on', 'on', 'on', 'off'],
  '8': ['on', 'on', 'on', 'on', 'off', 'off'],
  '9': ['on', 'on', 'on', 'off', 'off', 'off'],
  '10': ['on', 'on', 'off', 'off', 'off', 'off'],
  '11': ['on', 'off', 'off', 'off', 'off', 'off']
}

PHASE_NAMES = {
  'new': '0',
  'waxing_crescent': '1',
  'first_quarter': '3',
  'waxing_gibbous': '4',
  'full': '6',
  'waning_gibbous': '7',
  'last_quarter': '9',
  'waning_crescent': '11'
}