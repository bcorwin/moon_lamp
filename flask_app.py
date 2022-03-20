import os
import re
from time import sleep
from flask_wtf import FlaskForm
from subprocess import Popen, check_output, CalledProcessError
from flask import Flask, render_template_string, request, json
from wtforms import SubmitField, SelectField, IntegerField

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)


class SwitchForm(FlaskForm):
    # TODO: add screen selection (multi select)
    mode = SelectField("Mode:", choices=["on", "off", "timer", "day_only", "with_moon"])
    delay = IntegerField("Screen length (s):")
    timer_length = IntegerField("Timer length (hours):")
    submit = SubmitField('Submit')


home_template = '''
<head>
<link rel="shortcut icon" href="{{ url_for('static', filename='favicon.ico') }}">
</head>
{% if current_values %}
<b>Current</b><br><table>
{% for k,v in current_values.items() %}
    {% if v %}
        <tr><td>{{ k }}</td><td>{{ v }}</td></tr>
    {% endif %}
{% endfor %}
</table><hr>
{% endif %}
<form action="" method="post" novalidate>
    {{ form.hidden_tag() }}
    <p>{{ form.mode.label }} {{ form.mode() }}</p>
    <p>{{ form.delay.label }} {{ form.delay() }}</p>
    <p>{{ form.timer_length.label }} {{ form.timer_length() }}</p>
    <p>{{ form.submit() }}</p>
</form>
'''


def get_cmd(screens=[], mode=None, delay=None, timer_length=None):
    cmd = ["./set_lamp.sh"]
    for screen in screens:
        cmd += ["-s", screen]
    if mode:
        cmd += ["--mode", mode]
    if delay:
        cmd += ["--delay", delay]
    if timer_length:
        cmd += ["--timer-length", timer_length]

    return cmd


@app.route('/', methods=["GET", "POST"])
def moon_lamp_switch():
    if request.method == "POST":
        # needs validation
        form = request.form
        res = request.json
        if res is None:
            res = {}
        # Required
        mode = form.get("mode", res.get("mode", None))
        delay = form.get("delay", res.get("delay", None))
        timer_length = form.get("timer_length", res.get("timer_length", None))

        cmd = get_cmd(mode=mode, delay=delay, timer_length=timer_length)
        print(f"Running {' '.join(cmd)}")
        process = Popen(cmd)
        sleep(2)
        res = process.poll()
        if res is not None and res != 0:
            return "Unknown error, try again"
        return "Success!"

    form = SwitchForm()

    # Get current status
    # TODO: rename this file
    if os.path.exists("moonlamp.pid"):
        with open("moonlamp.pid", "r") as f:
            current_pid = int(f.read())
        try:
            current_status = check_output(["ps", "-f", "-p",  str(current_pid)]).decode()
        except CalledProcessError:
            current_status = ""
    else:
        current_status = ""

    current_values = {}
    for key in ["mode", "delay", "timer-length"]:
        value = re.search(rf"--{key} ([^\s]+)", current_status)
        if value:
            current_values[key] = value.group(1)

    return render_template_string(home_template, form=form, current_values=current_values)


@app.route('/watch/')
def watch():
    with open("lamp_html.txt") as f:
        lamp = f.read()
    return lamp


@app.route('/status/')
def status():
    if os.path.exists("moonlamp.pid"):
        with open("moonlamp.pid", "r") as f:
            current_pid = int(f.read())
        try:
            current_status = check_output(["ps", "-f", "-p", str(current_pid)]).decode()
        except CalledProcessError:
            current_status = ""
    else:
        current_status = ""

    current_values = {}
    for key in ["mode", "delay", "timer-length"]:
        value = re.search(rf"--{key} ([^\s]+)", current_status)
        if value:
            current_values[key] = value.group(1)
    current_values["mode"] = current_values.get("mode", "off")
    response = app.response_class(
        response=json.dumps(current_values),
        status=200,
        mimetype='application/json'
    )

    return response


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
