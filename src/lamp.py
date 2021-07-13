import os
import re

import colr
import inspect
from time import sleep
from requests import get
from dotenv import load_dotenv
from datetime import datetime, timedelta
try:
    import board
    import neopixel
except ModuleNotFoundError:
    pass

load_dotenv(override=True)


def gen_html(hex_color):
    style = f"fill:{hex_color};stroke-width:3;stroke:#000000"
    out = f'<svg width="20" height="20"><rect width="20" height="20" style="{style}"/></svg>'
    return out


def hour_rounder(t):
    # Rounds to nearest hour by adding a timedelta hour if minute >= 30
    return t.replace(second=0, microsecond=0, minute=0, hour=t.hour) + timedelta(hours=t.minute//30)


def contrast_color(color):
    color = tuple(int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
    luminance = (0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]) / 255
    return "#000000" if luminance > 0.5 else "#FFFFFF"


def get_phase_fraction(current_datetime):
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

    def _show_leds(self, colors):
        for i in range(len(colors)):
            color = colors[i]
            if self.pixel_order == "GRB":
                color = (color[1], color[0], color[2])
            led_idx = i if not self.reverse_leds else self.num_leds - i - 1
            self.pixels[led_idx] = color
        self.pixels.show()

    def catch_error(decorated):
        def wrapper(*args, **kwargs):
            func_name = decorated.__name__
            self = args[0]
            try:
                return decorated(*args, **kwargs)
            except Exception as e:
                self.show_error(f"Error on {func_name}: {str(e)}", div_id=func_name)
                return True

        return wrapper

    def show_error(self, msg, div_id):
        colors = 2 * [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        self.set_leds(colors, extra_info=msg, div_id=div_id)

    def leds_off(self):
        self.set_leds(self.num_leds*[(0, 0, 0)])

    def set_leds(self, colors, extra_info=None, blink=0, div_id=None):
        if div_id is None:
            div_id = inspect.stack()[1][3]
        assert self.num_leds == len(colors), f"Expecting {self.num_leds} colors not {len(colors)}"

        hex_colors = ['#%02x%02x%02x' % c for c in colors]
        current_time = str(datetime.now().replace(microsecond=0))

        print_string = [current_time]
        print_string.extend([colr.color(c, fore=contrast_color(c), back=c) for c in hex_colors])

        print_string_html = [f'<div id="{div_id}">{current_time}']
        print_string_html.extend([gen_html(c) for c in hex_colors])

        if extra_info:
            print_string += [extra_info]
            print_string_html += [extra_info]
        print_string = "\t".join(print_string)

        print_string_html[len(print_string_html)-1] += "</div>"
        print_string_html = "\t".join(print_string_html)
        
        with open("./lamp.txt", "w") as f:
            f.write(print_string)
            f.write("\n")

        html_file = []
        replaced = False
        with open("./lamp_html.txt", "r") as f:
            for line in f:
                if re.search(div_id, line):
                    html_file.append(print_string_html)
                    replaced = True
                else:
                    html_file.append(line.strip())
        if not replaced:
            html_file.append(print_string_html)
        html_file = "\n".join(html_file)
        with open("./lamp_html.txt", "w") as f:
            # TODO: completely re-write file occasionally (when turned off?) because the shown screens could change
            #  for example, cubs could no longer be playing OR still run set_leds but with print_only = True
            f.write(html_file)
            f.write("\n")

        if self.print_only:
            print(print_string)
        else:
            for _ in range(blink):
                self._show_leds(colors)
                sleep(0.25)
                self._show_leds(self.num_leds*[(0,0,0)])
                sleep(0.25)
            self._show_leds(colors)


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
        assert phase_number in self.phase_numbers, "Invalid phase_number"
        return self.phase_numbers[phase_number]

    def _set_lights(self, phase_number):
        # TODO: move this to show_moon so div_id is accurate
        light_status = self._get_light_status(phase_number)
        colors = [(255, 255, 255) if s == "on" else (0, 0, 50) for s in light_status]
        phase_name = {
            0: "New",
            1: "Waxing crescent", 2: "Waxing crescent",
            3: "First quarter",
            4: "Waxing gibbous", 5: "Waxing gibbous",
            6: "Full",
            7: "Waning gibbous", 8: "Waning gibbous",
            9: "Last quarter",
            10: "Waning crescent", 11: "Waning crescent",
        }.get(phase_number)
        self.set_leds(colors, extra_info=f"Current moon phase: {phase_name}")
        self.current_phase = phase_number
        return None

    @Lamp.catch_error
    def show_moon(self, phase_number=None):
        if not phase_number:
            phase_fraction = get_phase_fraction(datetime.utcnow())
            phase_number = get_phase_number(phase_fraction)

        self._set_lights(phase_number)
        return True


class WeatherLamp(Lamp):
    # TODO: find a way to flash between current and next hour/two hours/...
    api_key = os.getenv("WEATHER_API_KEY")
    lat = os.getenv("LAT")
    lon = os.getenv("LON")
    min_color = 0.1

    _raw_weather = {}
    _weather_updated_at = datetime(2020, 1, 1)

    def _update_weather(self):
        url = f"http://api.weatherapi.com/v1/forecast.json?key={self.api_key}&q={self.lat},{self.lon}&days=2"
        res = get(url)
        res.raise_for_status()

        weather = res.json()

        current_dt = datetime.now()
        nearest_hour = hour_rounder(current_dt)
        next_hour = nearest_hour + timedelta(hours=1)

        nearest_date_index = 0 if nearest_hour.day == current_dt.day else 1
        next_date_index = 0 if next_hour.day == current_dt.day else 1

        forecast1 = weather["forecast"]["forecastday"][nearest_date_index]["hour"][nearest_hour.hour]
        forecast2 = weather["forecast"]["forecastday"][next_date_index]["hour"][next_hour.hour]

        chance_of_rain = max(int(forecast1["chance_of_rain"]), int(forecast2["chance_of_rain"]))
        chance_of_snow = max(int(forecast1["chance_of_snow"]), int(forecast2["chance_of_snow"]))
        precip_mm = max(forecast1["precip_mm"], forecast2["precip_mm"])

        self._weather = {
            "clouds": weather["current"]["cloud"],
            "feels_like": weather["current"]["feelslike_f"],
            "chance_of_rain": chance_of_rain,
            "chance_of_snow": chance_of_snow,
            "precip_mm": precip_mm,

        }
        self._raw_weather = weather
        self._weather_updated_at = datetime.utcnow()

    def _get_weather(self, metric):
        if datetime.utcnow() - self._weather_updated_at > timedelta(minutes=15):
            self._update_weather()

        if metric == "cloudiness":
            return self._weather["clouds"]
        if metric == "feels_like":
            return self._weather["feels_like"]
        if metric == "precip":
            chance_of_rain = self._weather["chance_of_rain"]
            chance_of_snow = self._weather["chance_of_snow"]
            precip_amount = self._weather["precip_mm"]
            if chance_of_rain == 0 and chance_of_snow == 0:
                precip_type = None
                precip_percent = 0
            elif chance_of_snow >= chance_of_rain:
                precip_type = "snow"
                precip_percent = chance_of_snow
            elif chance_of_rain > chance_of_snow:
                precip_type = "rain"
                precip_percent = chance_of_rain
            return {
                "precip_percent": precip_percent,
                "precip_type": precip_type,
                "precip_amount": precip_amount
            }
        else:
            raise ValueError(f"unknown metric: {metric}")

    @Lamp.catch_error
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
        self.set_leds(colors, extra_info=f"{cloudiness}% cloudy")
        return True

    @Lamp.catch_error
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

        self.set_leds(colors, extra_info=f"It currently feels like {feels_like}F")
        return True

    @Lamp.catch_error
    def show_precipitation(self, precip_percent=None, precip_type=None, precip_amount=None):
        if precip_percent is None and precip_type is None and precip_amount is None:
            precip_forecast = self._get_weather("precip")
            precip_percent = precip_forecast["precip_percent"]
            precip_type = precip_forecast["precip_type"]
            precip_amount = precip_forecast["precip_amount"]

        if precip_type == "snow":
            base_color = (238, 130, 238)  # Violet
            blink = 0
            intensity = ""
        else:
            base_color = (75, 0, 130)  # Indigo
            if precip_amount > 7.6:
                blink = 4
                intensity = "intense "
            elif precip_amount > 2.5:
                blink = 2
                intensity = "heavy "
            else:
                blink = 0
                intensity = "light "

        full_leds = round(precip_percent / (100 / self.num_leds))

        colors = full_leds*[base_color]
        if len(colors) < self.num_leds:
            for i in range(self.num_leds - len(colors)):
                colors += [(0, 0, 0)]
        if full_leds > 0:
            text = f"There's a {precip_percent}% chance of {intensity}{precip_type} in the next two hours"
            self.set_leds(colors, extra_info=text, blink=blink)
            return True
        else:
            return False


class SportsLamp(Lamp):
    api_key = os.getenv("SPORTS_RADAR_KEY")

    _venue = "Wrigley Field"
    _game = None
    _schedule_updated_at = datetime(2020, 1, 1)
    _blue = (14, 51, 134)
    _red = (204, 52, 51)

    def _update_schedule(self):
        url = "http://statsapi.mlb.com/api/v1/schedule/games/?sportId=1"
        res = get(url)
        res.raise_for_status()

        schedule = res.json()["dates"]
        if len(schedule) == 0:
            game_status = 'no_game'
        else:
            schedule = schedule[0]
            games = {x['venue']['name']: x['dayNight'] for x in schedule["games"]}
            game = games.get(self._venue)
            game_status = game[0].upper() if game is not None else 'no_game'

        self._game = game_status

    def _get_game(self):
        if datetime.utcnow() - self._schedule_updated_at > timedelta(hours=6):
            self._update_schedule()
        return self._game

    @Lamp.catch_error
    def show_game(self, game=None):
        game_status = self._get_game() if game is None else game
        assert game_status in ("D", "N", "no_game"), "Invalid game status"

        if game_status == "D":
            colors = 3*[self._red] + 3*[self._blue]
            text = "There's a Cubs game today"
        elif game_status == "N":
            colors = 3*[self._blue] + 3*[self._red]
            text = "There's a Cubs game tonight"
        elif game_status == "no_game":
            colors = 6 * [(0, 0, 0)]
            text = "There's no Cubs game today"
        else:
            colors = 3*[self._red, self._blue]

        if game_status != 'no_game':
            self.set_leds(colors, extra_info=text)
            return True
        else:
            return False


if __name__ == "__main__":
    pass
