# TODO: daily cron job to save phase number to a file
# TODO: daily cron job to turn lights on to above phase
# TODO: daily cron job to turn light off
# TODO: (future) sync on/off jobs to moon rise/set
# TODO: (future) flask app to set modes
# TODO: (future) phase modes - current, fixed phase, cycle
# TODO: (future) light modes - on, off, with moon, on during time period
import datetime as dt
try:
    import board
    import neopixel
    PRINT_ONLY = False
except ModuleNotFoundError:
    PRINT_ONLY = True


if not PRINT_ONLY:
    pixel_pin = board.D18
    num_pixels = 6
    pixel_order = neopixel.GRB

    PIXELS = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=1, auto_write=False, pixel_order=pixel_order)

PHASE_NAMES = [
    ("New", 0.033863193308711),
    ("Waxing Crescent", 0.216136806691289),
    ("First Quarter", 0.283863193308711),
    ("Waxing Gibbous", 0.466136806691289),
    ("Full", 0.533863193308711),
    ("Waning Gibbous", 0.716136806691289),
    ("Last Quarter", 0.783863193308711),
    ("Waning Crescent", 0.966136806691289),
    ("New", 1),
]

PHASE_NUMBERS = {
    -1: ['on', 'off', 'on', 'off', 'on', 'off'],
    0: ['off', 'off', 'off', 'off', 'off', 'off'],
    1: ['off', 'off', 'off', 'off', 'off', 'on'],
    2: ['off', 'off', 'off', 'off', 'on', 'on'],
    3: ['off', 'off', 'off', 'on', 'on', 'on'],
    4: ['off', 'off', 'on', 'on', 'on', 'on'],
    5: ['off', 'on', 'on', 'on', 'on', 'on'],
    6: ['on', 'on', 'on', 'on', 'on', 'on'],
    7: ['on', 'on', 'on', 'on', 'on', 'off'],
    8: ['on', 'on', 'on', 'on', 'off', 'off'],
    9: ['on', 'on', 'on', 'off', 'off', 'off'],
    10: ['on', 'on', 'off', 'off', 'off', 'off'],
    11: ['on', 'off', 'off', 'off', 'off', 'off']
}

REVERSE = True


def get_phase_fraction(current_datetime=dt.datetime.utcnow()):
    # https://minkukel.com/en/various/calculating-moon-phase/
    lunar_cycle = 29.53058770576 * 24 * 3600  # Days to seconds
    first_new = dt.datetime(2000,1, 6, 18,14)

    phase_fraction = ((current_datetime - first_new).total_seconds() % lunar_cycle) / lunar_cycle

    return phase_fraction


def get_phase_name(phase_fraction):
    assert 0 <= phase_fraction <=1, f"Invalid phase_fraction: {phase_fraction}"

    for phase_name, max_value in PHASE_NAMES:
        if phase_fraction <= max_value:
            return phase_name


def get_phase_number(phase_fraction):
    """
    :param phase_fraction: The fraction of the moon that's illuminated (0 to 1)
    :return: The phase number for the lamp (which can display 12 different phases) 0 to 11
    """
    assert 0 <= phase_fraction <=1, f"Invalid phase_fraction: {phase_fraction}"
    phase_number = round(12*phase_fraction) % 12
    return phase_number


def get_light_status(phase_number):
    return PHASE_NUMBERS[phase_number]


def set_lights(phase_number):
    light_status = get_light_status(phase_number)
    if PRINT_ONLY:
        with open("lamp.txt", "w") as f:
            f.write(", ".join(light_status))
            f.write("\n")
    else:
        for i in range(len(light_status)):
            switch = light_status[i]
            leds = (255, 255, 255) if switch == "on" else (0, 0, 0)
            led_idx = i if not REVERSE else 5 - i
            PIXELS[led_idx] = leds
        PIXELS.show()

    return None


if __name__ == "__main__":
    pass
