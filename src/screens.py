import os
from time import sleep
from requests import get
from dotenv import load_dotenv
from datetime import datetime, timedelta, time

load_dotenv(override=True)


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
        if results[i][1] < datetime.now() <= results[i + 1][1]:
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


def sleep_until(dt):
    sleep_length = (dt - datetime.now()).total_seconds()
    sleep_length = max(0, sleep_length)
    print(f"Sleeping until {dt}")
    sleep(sleep_length)


class Screen:
    def __init__(self, obj, method, *args, **kwargs):
        self.method_to_call = getattr(obj, method)
        self.off = getattr(obj, "leds_off")
        self.args = args
        self.kwargs = kwargs

    def show_screen(self):
        return self.method_to_call(*self.args, **self.kwargs)


class Screens:
    def __init__(self, screens, delay=5):
        self.on_hour = 8
        self.off_hour = 21
        self.off = screens[0].off
        self.screens = screens
        self.delay = delay

    def show_screens(self, mode="on", timer_length=1):
        lamp_on = True

        if mode == "on":
            on_at = datetime.now()
            off_at = on_at + timedelta(days=1000)
        elif mode == "off":
            self.off()
            return None
        elif mode == "timer":
            on_at = datetime.now()
            off_at = on_at + timedelta(minutes=timer_length)
        elif mode == "day_only":
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
        elif mode == "with_moon":
            on_at, off_at, lamp_on = get_moon_times()
        else:
            raise ValueError(f"Invalid value for mode: {mode}")

        print(f"Initial on at: {on_at}")
        print(f"Initial off at: {off_at}")

        if not lamp_on:
            self.off()
        while True:
            current_dt = datetime.now()
            if on_at <= current_dt < off_at:
                lamp_on = True
                for screen in self.screens:
                    displayed = screen.show_screen()
                    if displayed:
                        sleep(self.delay)
            else:
                if mode == "timer":
                    self.off()
                    break
                elif lamp_on and mode == "day_only":
                    on_at = get_switch_datetime(self.on_hour, True)
                    off_at = get_switch_datetime(self.off_hour, True)
                    print(f"Next on at: {on_at}")
                    print(f"Next off at: {off_at}")
                elif lamp_on and mode == "with_moon":
                    on_at, off_at, _ = get_moon_times()
                    print(f"Next on at: {on_at}")
                    print(f"Next off at: {off_at}")
                self.off()
                lamp_on = False
                sleep_until(on_at)
