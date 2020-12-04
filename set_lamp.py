#!/usr/bin/env python3

import click
import moon_lamp as ml
from time import sleep

CURRENT_PHASE = -1


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


@click.command()
@click.option('--phase-mode', help='How to determine which phase to show')
@click.option('--phase-number', help='Internal phase number (0-11)')
@click.option('--phase-length', default=5, help='How long (in seconds) to to stay on a phase (only used in cycle mode)')
def set_lamp(phase_mode, phase_number, phase_length):
    if phase_mode == 'cycle':
        sleep_len = int(phase_length)
    elif phase_mode == 'current':
        sleep_len = 43200
    else:
        sleep_len = None

    while True:
        phase_number = get_phase(phase_mode, phase_number)
        ml.set_lights(phase_number)
        if not sleep_len:
            break
        else:
            sleep(sleep_len)


if __name__ == "__main__":
    set_lamp()
