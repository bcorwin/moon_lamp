from flask import render_template
from app import app
from app.forms import MoonLampConfigForm

@app.route('/edit')
def index():
    form = MoonLampConfigForm()
    return render_template('moon_lamp_config.html', title='Moon Lamp', form=form)
