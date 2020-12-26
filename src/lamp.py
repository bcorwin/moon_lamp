import os
import colr
from time import sleep
from requests import get
from dotenv import load_dotenv
from datetime import datetime, timedelta, time
try:
    import board
    import neopixel
except ModuleNotFoundError:
    pass

load_dotenv(override=True)


def contrast_color(color):
    color = tuple(int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
    luminance = (0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]) / 255
    return "#000000" if luminance > 0.5 else "#FFFFFF"


def get_phase_fraction(current_datetime=datetime.utcnow()):
    # https://minkukel.com/en/various/calculating-moon-phase/
    lunar_cycle = 29.53058770576 * 24 * 3600  # Days to seconds
    first_new = datetime(2000, 1, 6, 18, 14)

    phase_fraction = ((current_datetime - first_new).total_seconds() % lunar_cycle) / lunar_cycle

    return phase_fraction


def get_phase_number(phase_fraction):
    """
    :param phase_fraction: The fraction of the moon that's illuminated (0 to 1)
    :return: The phase number for the lamp (which can display 12 different phases) 0 to 11
    """
    assert 0 <= phase_fraction <=1, f"Invalid phase_fraction: {phase_fraction}"
    phase_number = round(12*phase_fraction) % 12
    return phase_number


class Lamp:
    def __init__(self,
                 print_only=(os.getenv("PRINT_ONLY") == 'True'),
                 reverse_leds=(os.getenv("REVERSE_LEDS") == 'True'),
                 num_leds=int(os.getenv("NUM_LEDS"))):
        if not print_only:
            pixel_pin = board.D18
            pixel_order = neopixel.GRB

            self.pixels = neopixel.NeoPixel(pixel_pin, num_leds, brightness=1,
                                            auto_write=False, pixel_order=pixel_order)
            self.pixel_order = pixel_order
        else:
            self.pixels = None
            self.pixel_order = "RGB"

        self.reverse_leds = reverse_leds
        self.print_only = print_only
        self.num_leds = num_leds

    def leds_off(self):
        self.set_leds(self.num_leds*[(0, 0, 0)])

    def set_leds(self, colors, extra_info=None):
        assert self.num_leds == len(colors), f"Expecting {self.num_leds} colors not {len(colors)}"

        hex_colors = ['#%02x%02x%02x' % c for c in colors]
        print_string = [str(datetime.now())]
        print_string.extend([colr.color(c, fore=contrast_color(c), back=c) for c in hex_colors])
        if extra_info:
            print_string += [extra_info]
        print_string = "\t".join(print_string)
        print(print_string)
        with open("./lamp.txt", "w") as f:
            f.write(str(datetime.now()))
            f.write("\t")
            f.write("\t".join(hex_colors))
            if extra_info:
                f.write("\t")
                f.write(extra_info)
            f.write("\n")

        if not self.print_only:
            for i in range(len(colors)):
                color = colors[i]
                if self.pixel_order == "GRB":
                    color = (color[1], color[0], color[2])
                led_idx = i if not self.reverse_leds else self.num_leds - i - 1
                self.pixels[led_idx] = color
            self.pixels.show()


class MoonLamp(Lamp):
    on_hour = 8
    off_hour = 20
    phase_numbers = {
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

    def _set_lights(self, phase_number):
        light_status = self._get_light_status(phase_number)
        colors = [(255, 255, 255) if s == "on" else (0, 0, 50) for s in light_status]
        self.set_leds(colors, extra_info=f"phase_number={phase_number}")
        self.current_phase = phase_number
        return None

    def show_moon(self, phase_number=None):
        if not phase_number:
            phase_fraction = get_phase_fraction()
            phase_number = get_phase_number(phase_fraction)

        self._set_lights(phase_number)


class WeatherLamp(Lamp):
    api_key = os.getenv("OPEN_WEATHER_KEY")
    lat = os.getenv("LAT")
    lon = os.getenv("LON")
    min_color = 0.1

    weather = {}
    weather_updated_at = datetime(2020, 1, 1)

    def _update_weather(self):
        url = "https://api.openweathermap.org/data/2.5/onecall"
        url += f"?lat={self.lat}&lon={self.lon}&appid={self.api_key}&units=imperial"
        res = get(url)
        self.weather = res.json()
        self.weather_updated_at = datetime.utcnow()

    def _get_weather(self, metric):
        if datetime.utcnow() - self.weather_updated_at > timedelta(minutes=15):
            self._update_weather()

        if metric == "cloudiness":
            return self.weather["current"]["clouds"]
        if metric == "feels_like":
            return self.weather["current"]["feels_like"]
        if metric == "precipitation":
            next_hour = self.weather['hourly'][0]  # TODO: Might not always be the first one
            precip_percent = next_hour.get("pop", 0)
            if "rain" in next_hour:
                precip_type = "rain"
                precip_volume = next_hour["rain"]["1h"]
        else:
            raise ValueError(f"unknown metric: {metric}")

    def show_sunniness(self, cloudiness=None):
        base_color = (255, 255, 0)
        if cloudiness is None:
            cloudiness = self._get_weather("cloudiness")
        sunniness = (100 - cloudiness) / (100 / self.num_leds)

        full_leds = int(sunniness)
        partial_led = sunniness - full_leds
        if full_leds == 0 and partial_led < self.min_color:
            partial_led = self.min_color

        colors = full_leds*[base_color]
        if partial_led > 0:
            colors += [tuple(int(partial_led * v) for v in base_color)]
        if len(colors) < self.num_leds:
            for i in range(self.num_leds - len(colors)):
                colors += [(0, 0, 0)]
        self.set_leds(colors, extra_info=f"cloudiness={cloudiness}")

    def show_feels_like(self, feels_like=None):
        if feels_like is None:
            feels_like = self._get_weather("feels_like")

        if feels_like < 20:
            base_color = (0, 191, 255)
            temp_range = (-10, 20)
        elif feels_like < 50:
            base_color = (0, 0, 255)
            temp_range = (20, 50)
        elif feels_like < 80:
            base_color = (0, 255, 0)
            temp_range = (50, 80)
        elif feels_like < 110:
            base_color = (255, 165, 0)
            temp_range = (80, 110)
        elif feels_like >= 110:
            base_color = (255, 0, 0)
            temp_range = (110, 130)

        if temp_range[0] <= feels_like < temp_range[1]:
            num_full_leds = int((feels_like - temp_range[0]) / 5) + 1
            colors = num_full_leds*[base_color] + (self.num_leds - num_full_leds)*[(0, 0, 0)]
        else:
            colors = 2*[base_color, (0, 0, 0), base_color]

        self.set_leds(colors, extra_info=f"feels_like={feels_like}")


if __name__ == "__main__":
    pass
