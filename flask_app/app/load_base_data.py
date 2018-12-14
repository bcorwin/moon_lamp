from app import db
from app.models import ErrorCode

error_codes = [
  {
    'error_code': 0,
    'description': 'phase_mode not defined',
    'light_pattern': 42
  },
  {
    'error_code': 1,
    'description': 'moon_times not available',
    'light_pattern': 12
  },
  {
    'error_code': 2,
    'description': 'lamp_mode not defined',
    'light_pattern': 21
  },
  {
    'error_code': 3,
    'description': 'Invalid phase number. Is moon info updated?',
    'light_pattern': 30
  },
]

for i in error_codes:
    e = ErrorCode(
        error_code=i["error_code"],
        description=i["description"],
        light_pattern=i["light_pattern"])
    db.session.add(e)

db.session.commit()
