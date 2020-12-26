import os
from requests import get
from src.lamp import Lamp
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv(override=True)


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

    def show_cloud_cover(self, cloudiness=None):
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
        self.set_leds(colors)

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

        self.set_leds(colors)


if __name__ == "__main__":
    pass
