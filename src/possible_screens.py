from src import lamp
from src.screens import Screen

weather_lamp = lamp.WeatherLamp()
moon_lamp = lamp.MoonLamp()

# Weather lamp screens
feels_like_screen = Screen(weather_lamp, "show_feels_like")
sunniness_screen = Screen(weather_lamp, "show_sunniness")

# Moon lamp screens
current_moon_screen = Screen(moon_lamp, "show_moon")

# Error screen
# TODO: Do this in a better way
error_screen = Screen(moon_lamp, "show_moon", phase_number=-1)