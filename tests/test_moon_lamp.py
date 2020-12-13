import moon_lamp as ml
from datetime import datetime, timedelta


def test_get_phase_fraction():
    # Be sure to use UTC
    # https://www.timeanddate.com/moon/phases/timezone/utc?year=2021

    new_moon = ml.get_phase_fraction(datetime(2020, 12, 14, 16, 16))
    assert round(new_moon, 1) == 0, "get_phase_fraction failed on new moon"

    first_quarter = ml.get_phase_fraction(datetime(2020, 12, 21, 23, 41))
    assert 0.2 < round(first_quarter, 2) < 0.3, "get_phase_fraction failed on first quarter"

    full_moon = ml.get_phase_fraction(datetime(2020, 12, 30, 3, 28))
    assert round(full_moon, 1) == 0.5, "get_phase_fraction failed on full moon"

    third_quarter = ml.get_phase_fraction(datetime(2021, 1, 6, 9, 37))
    assert 0.7 < round(third_quarter, 2) < 0.8, "get_phase_fraction failed on third quarter"


def test_get_phase_number():
    fractions_to_test = {
        0: 0, 1: 0,  # New Moon
        1/12: 1, 2/12: 2,  # Waxing crescent
        3/12: 3,  # First quarter
        4/12: 4, 5/12: 5,  # Waxing gibbous
        6/12: 6,  # First quarter
        7/12: 7, 8/12: 8,  # Waning crescent
        9/12: 9,  # Third quarter
        10/12: 10, 11/12: 11,  # Waning gibbous
    }
    for fraction, phase_number in fractions_to_test.items():
        assert ml.get_phase_number(fraction) == phase_number, f"get_phase_number failed on {fraction}"


def test_get_moon_times():
    dates_to_test = [datetime.today() + timedelta(hours=i*24) for i in range(31)]
    for date in dates_to_test:
        try:
            _ = ml.get_moon_times(date)
        except Exception as e:
            print(f"failed on {date}")
            raise e


class TestMoonLamp:
    def __init__(self):
        self.moon_lamp = ml.MoonLamp(print_only=True, reverse_leds=False)

    def run_test(self, expected_outcome, **kwargs):
        self.moon_lamp.set_lamp(**kwargs)
        with open("lamp.txt", "r") as f:
            output = f.read()
        output = output[27:][:-1]
        assert output == expected_outcome, f"MoonLamp.set_lamp() failed on {expected_outcome}: {kwargs}"


def test_moon_lamp():
    test = TestMoonLamp()

    test.run_test(6 * ["off"], phase_mode="fixed", phase_number=0)

