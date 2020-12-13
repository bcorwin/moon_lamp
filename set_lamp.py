#!/usr/bin/env python3
import os
import click
import moon_lamp as ml
from dotenv import load_dotenv

load_dotenv(override=True)

MOON_LAMP = ml.MoonLamp(print_only=os.getenv("PRINT_ONLY"), reverse_leds=os.getenv("REVERSE_LEDS"))


@click.command()
@click.option('--phase-mode', default="current", help='How to determine which phase to show')
@click.option('--phase-number', default=6, help='Internal phase number (0-11)')
@click.option('--phase-length', default=5, help='How long (in seconds) to to stay on a phase (only used in cycle mode)')
@click.option('--lamp-mode', default="on", help='How should the lamp turn on')
@click.option('--timer-length', default=1, help='In hours, how long the lamp should stay on (used in lamp mode= timer')
def set_lamp(phase_mode, phase_number, phase_length, lamp_mode, timer_length):
    MOON_LAMP.set_lamp(phase_mode, phase_number, phase_length, lamp_mode, timer_length)


if __name__ == "__main__":
    set_lamp()
