import os
from time import sleep
from requests import get
from dotenv import load_dotenv
from datetime import timedelta, time, datetime
try:
    import board
    import neopixel
except ModuleNotFoundError:
    pass

load_dotenv(override=True)


def get_phase_fraction(current_datetime=datetime.utcnow()):
    # https://minkukel.com/en/various/calculating-moon-phase/
    lunar_cycle = 29.53058770576 * 24 * 3600  # Days to seconds
    first_new = datetime(2020, 12, 14, 16, 16)

    phase_fraction = ((current_datetime - first_new).total_seconds() % lunar_cycle) / lunar_cycle

    return phase_fraction


def get_phase_number(phase_fraction):
    """
    :param phase_fraction: The fraction of the moon that's illuminated (0 to 1)
    :return: The phase number for the lamp (which can display 12 different phases) 0 to 11
    """
    assert 0 <= phase_fraction <= 1, f"Invalid phase_fraction: {phase_fraction}"
    phase_number = round(12 * phase_fraction) % 12
    return phase_number


def get_switch_datetime(hour, tomorrow=False):
    current_dt = datetime.now()
    if tomorrow:
        current_dt = current_dt + timedelta(hours=24)
    out = datetime(current_dt.year, current_dt.month, day=current_dt.day, hour=hour)
    return out


def get_moon_times(current_dt=datetime.now()):
    results = []
    for delta in [-24, 0, 24, 48]:
        date = current_dt + timedelta(hours=delta)
        res = get("https://api.ipgeolocation.io/astronomy",
                  params={"apiKey": os.getenv("API_KEY"), "date": date.strftime("%Y-%m-%d")})
        res.raise_for_status()
        data = res.json()

        for s in ["rise", "set"]:
            value = data.get(f"moon{s}")
            value = time(int(value[:2]), int(value[3:])) if value != '-:-' else None
            if value:
                value = datetime(year=date.year, month=date.month, day=date.day, hour=value.hour, minute=value.minute)
                results += [(s, value)]
    results = sorted(results, key=lambda x: x[1])

    for i in range(len(results)):
        if results[i][1] < current_dt <= results[i + 1][1]:
            if results[i][0] == "rise":
                moon_up = True
                moon_rise = results[i][1]
                moon_set = results[i+1][1]
            else:
                # Return next moon rise/set
                moon_up = False
                moon_rise = results[i+1][1]
                moon_set = results[i+2][1]
            break

    return moon_rise, moon_set, moon_up


class MoonLamp:
    def __init__(self, print_only, reverse_leds):
        if not print_only:
            pixel_pin = board.D18
            num_pixels = 6
            pixel_order = neopixel.GRB

            self.pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=1,
                                            auto_write=False, pixel_order=pixel_order)

        self.on_hour = 8
        self.off_hour = 20
        self.current_phase = 0
        self.reverse_leds = reverse_leds
        self.print_only = print_only
        self.phase_numbers = {
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

    def _get_light_status(self, phase_number):
        return self.phase_numbers[phase_number]

    def _get_phase(self, phase_mode, phase_number):
        if phase_mode == 'current':
            phase_fraction = get_phase_fraction()
            phase_number = get_phase_number(phase_fraction)
        elif phase_mode == 'fixed':
            phase_number = int(phase_number)
        elif phase_mode == 'cycle':
            phase_number = (self.current_phase + 1) % 12
        else:
            raise ValueError(f"Invalid phase_mode: {phase_mode}")
        return phase_number

    def _set_lights(self, phase_number):
        light_status = self._get_light_status(phase_number)
        if self.print_only:
            with open("lamp.txt", "w") as f:
                f.write(str(datetime.now()))
                f.write(" ")
                f.write(", ".join(light_status))
                f.write("\n")
        else:
            for i in range(len(light_status)):
                switch = light_status[i]
                leds = (255, 255, 255) if switch == "on" else (0, 0, 0)
                led_idx = i if not self.reverse_leds else 5 - i
                self.pixels[led_idx] = leds
            self.pixels.show()
            self.current_phase = phase_number
        return None

    def _lights_off(self):
        self.pixels.fill((0, 0, 0))
        return None

    def set_lamp(self, phase_mode="current", lamp_mode="on", phase_number=None, phase_length=None, timer_length=None):
        if phase_mode == 'cycle':
            sleep_len = int(phase_length)
        elif phase_mode in ('current', 'fixed'):
            sleep_len = 60 * 5
        else:
            raise ValueError(f"Invalid value for phase_mode: {phase_mode}")

        lamp_on = True
        on_at = off_at = None
        if lamp_mode == "on":
            on_at = datetime.now()
            off_at = on_at + timedelta(days=1000)
        elif lamp_mode == "timer":
            on_at = datetime.now()
            off_at = on_at + timedelta(hours=int(timer_length))
        elif lamp_mode == "day_only":
            current_dt = datetime.now()
            if time(self.on_hour) <= current_dt.time() < time(self.off_hour):
                on_at = get_switch_datetime(self.on_hour)  # 8am today
                off_at = get_switch_datetime(self.off_hour)  # 8pm today
            elif current_dt.time() < time(self.on_hour):
                lamp_on = False
                on_at = get_switch_datetime(self.on_hour)  # 8am today
                off_at = get_switch_datetime(self.off_hour)  # 8pm today
            elif time(self.off_hour) <= current_dt.time():
                lamp_on = False
                on_at = get_switch_datetime(self.on_hour, True)  # 8am tomorrow
                off_at = get_switch_datetime(self.off_hour, True)  # 8pm tomorrow
        elif lamp_mode == "with_moon":
            on_at, off_at, lamp_on = get_moon_times()
        else:
            raise ValueError(f"Invalid value for lamp_mode: {lamp_mode}")

        print(f"Initial on at: {on_at}")
        print(f"Initial off at: {off_at}")

        if not lamp_on:
            self._set_lights(0)
        while True:
            current_dt = datetime.now()
            if on_at <= current_dt < off_at:
                phase = self._get_phase(phase_mode, phase_number)
                lamp_on = True
                self._set_lights(phase)
            else:
                if lamp_mode == "timer":
                    sleep_len = None
                elif lamp_on and lamp_mode == "day_only":
                    on_at = get_switch_datetime(self.on_hour, True)
                    off_at = get_switch_datetime(self.off_hour, True)
                    print(f"Next on at: {on_at}")
                    print(f"Next off at: {off_at}")
                elif lamp_on and lamp_mode == "with_moon":
                    on_at, off_at, _ = get_moon_times()
                    print(f"Next on at: {on_at}")
                    print(f"Next off at: {off_at}")
                self._lights_off()
                lamp_on = False
            if sleep_len:
                sleep(sleep_len)
            else:
                break


if __name__ == "__main__":
    pass
