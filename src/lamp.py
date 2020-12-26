import colr
from datetime import datetime
try:
    import board
    import neopixel
except ModuleNotFoundError:
    pass


def contrast_color(color):
    color = tuple(int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
    luminance = (0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]) / 255
    return "#000000" if luminance > 0.5 else "#FFFFFF"


class Lamp:
    def __init__(self, print_only, reverse_leds, num_leds):
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

    def set_leds(self, colors):
        assert self.num_leds == len(colors), f"Expecting {self.num_leds} colors not {len(colors)}"

        hex_colors = ['#%02x%02x%02x' % c for c in colors]
        print_string = [str(datetime.now())]
        print_string.extend([colr.color(c, fore=contrast_color(c), back=c) for c in hex_colors])
        print_string = "\t".join(print_string)
        print(print_string)
        with open("./lamp.txt", "w") as f:
            f.write(str(datetime.now()))
            f.write("\t")
            f.write("\t".join(hex_colors))
            f.write("\n")

        if not self.print_only:
            for i in range(len(colors)):
                color = colors[i]
                if self.pixel_order == "GRB":
                    color = (color[1], color[0], color[2])
                led_idx = i if not self.reverse_leds else self.num_leds - i - 1
                self.pixels[led_idx] = color
            self.pixels.show()


if __name__ == "__main__":
    pass
