import os
import re
from time import sleep
from flask_wtf import FlaskForm
from subprocess import Popen, check_output, CalledProcessError
from flask import Flask, render_template_string, request
from wtforms import SubmitField, SelectField, IntegerField

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)


class SwitchForm(FlaskForm):
    phase_mode = SelectField("Phase mode:", choices=["current", "fixed", "cycle", "off"])
    phase_number = SelectField("Phase number:", choices=[None] + list(range(12)))
    phase_length = IntegerField("Phase length (seconds):")
    lamp_mode = SelectField("Lamp mode:", choices=["day_only", "on", "timer"])
    timer_length = IntegerField("Timer length (hours):")
    submit = SubmitField('Submit')


home_template = '''
<head>
<link rel="shortcut icon" href="{{ url_for('static', filename='favicon.ico') }}">
</head>
{% if current_values %}
<b>Current</b><br><table>
{% for k,v in current_values.items() %}
    <tr><td>{{ k }}</td><td>{{ v }}</td></tr>
{% endfor %}
</table><hr>
{% endif %}
<form action="" method="post" novalidate>
    {{ form.hidden_tag() }}
    <p>{{ form.phase_mode.label }} {{ form.phase_mode() }}</p>
    <p>{{ form.phase_number.label }} {{ form.phase_number() }}</p>
    <p>{{ form.phase_length.label }} {{ form.phase_length() }}</p>
    <p>{{ form.lamp_mode.label }} {{ form.lamp_mode() }}</p>
    <p>{{ form.timer_length.label }} {{ form.timer_length() }}</p>
    <p>{{ form.submit() }}</p>
</form>
'''


def get_cmd(phase_mode, lamp_mode, phase_number=None, phase_length=None, timer_length=None):
    cmd = ["./set_lamp.sh"]
    if phase_mode == "off":
        phase_mode = "fixed"
        phase_number = "0"
        phase_length = None

    cmd += [f"--phase-mode={phase_mode}"]
    if phase_number:
        cmd += [f"--phase-number={phase_number}"]
    if phase_length:
        cmd += [f"--phase-length={phase_length}"]
    cmd += [f"--lamp-mode={lamp_mode}"]
    if timer_length:
        cmd += [f"--timer-length={timer_length}"]

    return cmd


@app.route('/', methods=["GET", "POST"])
def moon_lamp_switch():
    if request.method == "POST":
        # needs validation
        form = request.form
        # Required
        phase_mode = form["phase_mode"]
        timer_length = form["timer_length"]

        phase_number = form["phase_number"]
        if phase_number in ('', 'None'):
            phase_number = None
        phase_length = form["phase_length"]
        if phase_length in ('', 'None'):
            phase_length = None
        lamp_mode = form["lamp_mode"]
        if timer_length in ('', 'None'):
            timer_length = None

        cmd = get_cmd(phase_mode, lamp_mode, phase_number, phase_length, timer_length)
        process = Popen(cmd)
        sleep(1)
        res = process.poll()
        if res is not None and res != 0:
            return "Unknown error, try again"
        return "Success!"

    form = SwitchForm()

    # Get current status
    with open("moonlamp.pid", "r") as f:
        current_pid = int(f.read())

    try:
        current_status = check_output(["ps", "-f", "-p",  str(current_pid)]).decode()
    except CalledProcessError:
        current_status = ""

    current_values = {}
    phase_mode = re.search(r"--phase-mode=([^\s]+)", current_status)
    if phase_mode:
        current_values["phase_mode"] = phase_mode.group(1)

    phase_number = re.search(r"--phase-number=([^\s]+)", current_status)
    if phase_number:
        current_values["phase_number"] = phase_number.group(1)

    phase_length = re.search(r"--phase-length=([^\s]+)", current_status)
    if phase_length:
        current_values["phase_length"] = phase_length.group(1)

    lamp_mode = re.search(r"--lamp-mode=([^\s]+)", current_status)
    if lamp_mode:
        current_values["lamp_mode"] = lamp_mode.group(1)

    timer_length = re.search(r"--timer-length=([^\s]+)", current_status)
    if timer_length:
        current_values["timer_length"] = timer_length.group(1)

    return render_template_string(home_template, form=form, current_values=current_values)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
