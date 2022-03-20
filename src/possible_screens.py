from src import lamp
from src.screens import Screen

weather_lamp = lamp.WeatherLamp()
moon_lamp = lamp.MoonLamp()
sports_lamp = lamp.SportsLamp()
color_lamp = lamp.ColorsLamp()

# Weather lamp screens
feels_like_screen = Screen(weather_lamp, "show_feels_like")
sunniness_screen = Screen(weather_lamp, "show_sunniness")
daily_precip_screen = Screen(weather_lamp, "show_precipitation")

# Moon lamp screens
current_moon_screen = Screen(moon_lamp, "show_moon")

# Sports lamp screens
game_today = Screen(sports_lamp, "show_game")

# Flags
ukraine_flag = Screen(color_lamp, "show_colors", colors=3*[(0, 87, 183)] + 3*[(255, 215, 0)])

# Error screen
# TODO: Do this in a better way
error_screen = Screen(moon_lamp, "show_moon", phase_number=-1)