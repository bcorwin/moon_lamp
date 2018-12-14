from app import db
from datetime import datetime

class ErrorCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    error_code = db.Column(db.Integer, unique=True, nullable=False)
    description = db.Column(db.String(100), nullable=False)
    light_pattern = db.Column(db.Integer, unique=True, nullable=False)

    def __repr__(self):
        return(f"<Error: {self.description} (ErrorCode={self.id})>")

class MoonPhase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), nullable=False)
    display_name = db.Column(db.String(16), nullable=False)
    light_pattern = db.Column(db.Integer, unique=True, nullable=False)

    def __repr__(self):
        return(f"<MoonPhase: {display_name} ({light_pattern})")

class MoonRiseTime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_at = db.Column(db.DateTime, unique=True, nullable=False)
    moon_phase_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return(f"<MoonRiseTime: {moon_phase_id} starts at {start_at}>")
