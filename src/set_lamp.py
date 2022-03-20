#!/usr/bin/env python3
import click
from src.screens import Screens
import src.possible_screens as ps


@click.command()
@click.option('-s', '--screen', multiple=True, default=["feels_like_screen", "sunniness_screen", "current_moon_screen",
                                                        "daily_precip_screen", "game_today", "ukraine_flag"],
              help='Screen to show (see src/possible_screens.py')
@click.option('-d', '--delay', default=5, help='How long, in seconds, to show each screen (default=5)')
@click.option('-m', '--mode', default="day_only", help='Which mode to use (default=day_only)')
@click.option('-t', '--timer-length', default=1,
              help='How long, in hours, to leave the lamp on in timer mode (default=1)')
def set_lamp(screen, delay, mode, timer_length):
    screens_to_show = [getattr(ps, s) for s in screen]
    screens = Screens(screens=screens_to_show, delay=delay)
    screens.show_screens(mode=mode, timer_length=timer_length)


if __name__ == "__main__":
    set_lamp()
