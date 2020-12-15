from datetime import datetime
try:
    import board
    import neopixel
except ModuleNotFoundError:
    pass


class Lamp:
    def __init__(self, print_only, reverse_leds, num_leds):
        if not print_only:
            pixel_pin = board.D18
            pixel_order = neopixel.GRB

            self.pixels = neopixel.NeoPixel(pixel_pin, num_leds, brightness=1,
                                            auto_write=False, pixel_order=pixel_order)
        else:
            self.pixels = None

        self.reverse_leds = reverse_leds
        self.print_only = print_only
        self.num_leds = num_leds

    def leds_off(self):
        self.set_leds(self.num_leds*[(0, 0, 0)])

    def set_leds(self, colors):
        assert self.num_leds == len(colors), f"Expecting {self.num_leds} colors not {len(colors)}"

        if self.print_only:
            colors = ['#%02x%02x%02x' % c for c in colors]
            with open("./lamp.txt", "w") as f:
                f.write(str(datetime.now()))
                f.write("\t")
                f.write("\t".join(colors))
                f.write("\n")
        else:
            for i in range(len(colors)):
                color = colors[i]
                led_idx = i if not self.reverse_leds else self.num_leds - i - 1
                self.pixels[led_idx] = color
            self.pixels.show()


if __name__ == "__main__":
    pass
