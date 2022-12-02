import re
import json
import pathlib

class CreateRGB:
    """This class has several methods for converting a
    string-encoded color to its RGB-tuple representation.
    """

    def __init__(self):
        """The constructor loads the CSS color codes from `codes.json`."""
        self.color_codes = json.load(open(pathlib.Path(__file__).parent / 'codes.json', 'r'))

    def from_hex(self, string):
        """This function takes as input the hex representation of a color
        (`#rgb` or `#rrggbb`) and returns its RGB-tuple equivalent
        or `None` if the given string doesn't follow the right format.
        """
        if re.match(r'#[0-9a-fA-F]{3}$', string):
            r = string[1]
            g = string[2]
            b = string[3]
            return self.from_hex(f'#{r}{r}{g}{g}{b}{b}')
        if re.match(r'#[0-9a-fA-F]{6}$', string):
            r = string[1:3]
            g = string[3:5]
            b = string[5:7]
            return int(r, 16), int(g, 16), int(b, 16)

    def from_rgb(self, string):
        """This function takes as input the functional-RGB representation
        of a color (`rgb(r, g, b)`) and returns its RGB-tuple equivalent
        or `None` if the given string doesn't follow the right format.
        """
        match = re.match(r'rgb *\( *(?P<r>\d{1,3}) *, *(?P<g>\d{1,3}) *, *(?P<b>\d{1,3}) *\)$', string)
        if match:
            return (
                int(match.groupdict()['r']),
                int(match.groupdict()['g']),
                int(match.groupdict()['b'])
            )

    def from_css(self, string):
        """This function takes as input a CSS color-keyword and returns its
        RGB-tuple equivalent or `None` if the given color-keyword doesn't exist.
        """
        if string in self.color_codes:
            return self.from_hex(self.color_codes[string])

    def from_string(self, string):
        """This function takes a string-encoded color and returns
        its RGB-tuple representation or `None` if it doesn't follow
        one of the `hex`, `rgb` or `css` formats.
        """
        rgb = None
        rgb = rgb or self.from_hex(string)
        rgb = rgb or self.from_rgb(string)
        rgb = rgb or self.from_css(string)
        return rgb
