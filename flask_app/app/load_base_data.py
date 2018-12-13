from app import db
from app.models import ErrorCode

# DO NOT CHANGE THE ORDER OF THE BELOW ERRORS
error_codes = [
  {
    'description': 'phase_mode not defined',
    'light_pattern': 42
  },
  {
    'description': 'moon_times not available',
    'light_pattern': 12
  },
  {
    'description': 'lamp_mode not defined',
    'light_pattern': 21
  },
  {
    'description': 'Invalid phase number. Is moon info updated?',
    'light_pattern': 30
  },
]

for i in error_codes:
    e = ErrorCode(description=i["description"], light_pattern=i["light_pattern"])
    db.session.add(e)

db.session.commit()
