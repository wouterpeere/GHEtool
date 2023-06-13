"""
script to define the GUI colors
"""

from matplotlib.colors import to_rgb
from numpy import array, float64

WHITE: str = "rgb(255, 255, 255)"
LIGHT: str = "rgb(84, 188, 235)"
LIGHT_SELECT: str = "rgb(42, 126, 179)"
DARK: str = "rgb(0, 64, 122)"
GREY: str = "rgb(100, 100, 100)"
WARNING: str = "rgb(255, 200, 87)"
BLACK: str = "rgb(0, 0, 0)"

dark_matplotlib: str = to_rgb(
    array(DARK.replace('rgb(', '').replace(')', '').split(','), dtype=float64) / 255)
white_matplotlib: str = to_rgb(
    array(WHITE.replace('rgb(', '').replace(')', '').split(','), dtype=float64) / 255)
light_matplotlib: str = to_rgb(
    array(LIGHT.replace('rgb(', '').replace(')', '').split(','), dtype=float64) / 255)
bright_matplotlib: str = to_rgb(
    array(WARNING.replace('rgb(', '').replace(')', '').split(','), dtype=float64) / 255)
