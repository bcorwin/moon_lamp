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
    submit = SubmitField('Submit')


home_template = '''
{% if phase_mode %} Current phase_mode: {{ phase_mode }} <br> {% endif %}
{% if phase_number %} Current phase_number: {{ phase_number }} <br> {% endif %}
{% if phase_length %} Current phase_length: {{ phase_length }} <br> {% endif %}
{% if phase_mode %} <hr> {% endif %}
<form action="" method="post" novalidate>
    {{ form.hidden_tag() }}
    <p>{{ form.phase_mode.label }} {{ form.phase_mode() }}</p>
    <p>{{ form.phase_number.label }} {{ form.phase_number() }}</p>
    <p>{{ form.phase_length.label }} {{ form.phase_length() }}</p>
    <p>{{ form.submit() }}</p>
</form>
'''


def get_cmd(phase_mode, phase_number=None, phase_length=None):
    cmd = ["sudo", "./set_lamp.sh"]
    if phase_mode == "off":
        phase_mode = "fixed"
        phase_number = "0"
        phase_length = None

    cmd += [f"--phase-mode={phase_mode}"]
    if phase_number:
        cmd += [f"--phase-number={phase_number}"]
    if phase_length:
        cmd += [f"--phase-length={phase_length}"]

    return cmd


@app.route('/', methods=["GET", "POST"])
def moon_lamp_switch():
    if request.method == "POST":
        # needs validation
        form = request.form
        phase_mode = form["phase_mode"]
        phase_number = form["phase_number"]
        if phase_number in ('', 'None'):
            phase_number = None
        phase_length = form["phase_length"]
        if phase_length in ('', 'None'):
            phase_length = None

        cmd = get_cmd(phase_mode, phase_number, phase_length)
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
        print(current_pid)
        current_status = check_output(["ps", "-p", str(current_pid)]).decode()

    except CalledProcessError:
        current_status = ""
        print("Not running")

    phase_mode = re.search(r"--phase-mode=([^\s]+)", current_status)
    if phase_mode:
        phase_mode = phase_mode.group(1)

    phase_number = re.search(r"--phase-number=([^\s]+)", current_status)
    if phase_number:
        phase_number = phase_number.group(1)

    phase_length = re.search(r"--phase-length=([^\s]+)", current_status)
    if phase_length:
        phase_length = phase_length.group(1)

    return render_template_string(home_template, form=form,
                                  phase_mode=phase_mode, phase_length=phase_length, phase_number=phase_number)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)