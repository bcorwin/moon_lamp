from app import db

class ErrorCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100))
    light_pattern = db.Column(db.Integer, unique=True)

    def __repr__(self):
        return(f"<Error: {self.description} (ErrorCode = {self.id})>")

class MoonPhase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16))
    display_name = db.Column(db.String(16))
    light_pattern = db.Column(db.Integer, unique=True)

    def __repr__(self):
        return(f"<MoonPhase: {display_name} ({light_pattern})")
