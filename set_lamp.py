#!/usr/bin/env python3

import click
import moon_lamp as ml
from time import sleep
from datetime import datetime as dt
from datetime import timedelta, time, datetime

CURRENT_PHASE = -1
ON_HOUR = 8
OFF_HOUR = 20


def get_phase(phase_mode, phase_number):
    global CURRENT_PHASE

    if phase_mode == 'current':
        phase_fraction = ml.get_phase_fraction()
        phase_number = ml.get_phase_number(phase_fraction)
    elif phase_mode == 'fixed':
        phase_number = int(phase_number)
    elif phase_mode == 'cycle':
        phase_number = (CURRENT_PHASE + 1) % 12
    else:
        raise ValueError(f"Invalid phase_mode: {phase_mode}")
    CURRENT_PHASE = phase_number
    return phase_number


def get_switch_datetime(hour, tomorrow=False):
    current_dt = dt.now()
    if tomorrow:
        current_dt = current_dt + timedelta(hours=24)
    out = datetime(current_dt.year, current_dt.month, day=current_dt.day, hour=hour)
    return out


@click.command()
@click.option('--phase-mode', help='How to determine which phase to show')
@click.option('--phase-number', help='Internal phase number (0-11)')
@click.option('--phase-length', default=5, help='How long (in seconds) to to stay on a phase (only used in cycle mode)')
@click.option('--lamp-mode', default="on", help='How should the lamp turn on')
@click.option('--timer-length', default=1, help='In hours, how long the lamp should stay on (used in lamp mode= timer')
def set_lamp(phase_mode, phase_number, phase_length, lamp_mode, timer_length):
    if phase_mode == 'cycle':
        sleep_len = int(phase_length)
    elif phase_mode in ('current', 'fixed'):
        sleep_len = 60*5
    else:
        raise ValueError(f"Invalid value for phase_mode: {phase_mode}")

    lamp_on = True
    if lamp_mode == "on":
        on_at = dt.now()
        off_at = on_at + timedelta(days=1000)
    elif lamp_mode == "timer":
        on_at = dt.now()
        off_at = on_at + timedelta(hours=int(timer_length))
    elif lamp_mode == "day_only":
        current_dt = dt.now()
        if time(ON_HOUR) <= current_dt.time() < time(OFF_HOUR):
            on_at = get_switch_datetime(ON_HOUR)  # 8am today
            off_at = get_switch_datetime(OFF_HOUR)  # 8pm today
        elif current_dt.time() < time(ON_HOUR):
            lamp_on = False
            on_at = get_switch_datetime(ON_HOUR)  # 8am today
            off_at = get_switch_datetime(OFF_HOUR)  # 8pm today
        elif time(OFF_HOUR) <= current_dt.time():
            lamp_on = False
            on_at = get_switch_datetime(ON_HOUR, True)  # 8am tomorrow
            off_at = get_switch_datetime(OFF_HOUR, True)  # 8pm tomorrow
        print(f"Initial on at: {on_at}")
        print(f"Initial off at: {off_at}")
    else:
        raise ValueError(f"Invalid value for lamp_mode: {lamp_mode}")

    if not lamp_on:
        ml.set_lights(0)
    while True:
        current_dt = dt.now()
        if on_at <= current_dt < off_at:
            phase = get_phase(phase_mode, phase_number)
            lamp_on = True
        else:
            phase = 0  # Off
            if lamp_mode == "timer":
                sleep_len = None
            elif lamp_on and lamp_mode == "day_only":
                on_at = get_switch_datetime(ON_HOUR, True)
                off_at = get_switch_datetime(OFF_HOUR, True)
                print(f"Next on at: {on_at}")
                print(f"Next off at: {off_at}")
            lamp_on = False
        ml.set_lights(phase)
        if sleep_len:
            sleep(sleep_len)
        else:
            break


if __name__ == "__main__":
    set_lamp()
