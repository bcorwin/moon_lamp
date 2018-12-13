from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired

phase_modes = [("current", "Current"), ("hold", "Hold")]
phases = [
    ("new", "New"),
    ("waxing_crescent", "Waxing crescent"),
    ("first_quarter", "First quarter"),
    ("waxing_gibbous", "Waxing gibbous"),
    ("full", "Full"),
    ("waning_gibbous", "Waning gibbous"),
    ("last_quarter", "Last quarter"),
    ("waning_crescent", "Waning crescent")
]

lamp_modes = [("on", "On"), ("off", "Off"), ("with_moon", "With moon")]

class MoonLampConfigForm(FlaskForm):
    phase_mode = SelectField("Mode", choices = phase_modes)
    #phase_time =
    phase_phase = SelectField("Phase", choices = phases)

    lamp_mode = SelectField("Lamp", choices = lamp_modes)
    #lamp_time

    submit = SubmitField('Update')
