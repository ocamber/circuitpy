# SPDX-FileCopyrightText: 2019 Melissa LeBlanc-Williams for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
This is a Conference Badge type Name Tag that is intended to be displayed on
the PyBadge. Feel free to customize it to your heart's content.
"""

from math import sqrt, cos, sin, radians
import board
from micropython import const
import displayio
import neopixel
from keypad import ShiftRegisterKeys, Event
from adafruit_display_shapes.rect import Rect
from adafruit_display_text.label import Label
from adafruit_bitmap_font import bitmap_font

# Button Constants
BUTTON_LEFT = const(7)
BUTTON_UP = const(6)
BUTTON_DOWN = const(5)
BUTTON_RIGHT = const(4)
BUTTON_SEL = const(3)
BUTTON_START = const(2)
BUTTON_A = const(1)
BUTTON_B = const(0)
NAME_STRINGS = ("OREN","אורן","ΩΡΕΝ","ОРЕН","اورن")

FONT_NAMES = ("English","Hebrew","Greek","Russian","Arabic")

# Customizations
NEOPIXEL_COUNT = 5
BACKGROUND_COLOR = 0xFF0000
FOREGROUND_COLOR = 0xFFFFFF
BACKGROUND_TEXT_COLOR = 0xFFFFFF
FOREGROUND_TEXT_COLOR = 0x000000

settings = {"brightness": 0.05, "direction": 1, "speed": 1}

# Define the NeoPixel
neopixels = neopixel.NeoPixel(
    board.NEOPIXEL,
    NEOPIXEL_COUNT,
    brightness=settings["brightness"],
    auto_write=False,
    pixel_order=neopixel.GRB,
)

# Define Events and Shift Register
event = Event()
last_event = Event()

pad = ShiftRegisterKeys(
    clock=board.BUTTON_CLOCK,
    data=board.BUTTON_OUT,
    latch=board.BUTTON_LATCH,
    key_count=8,
    value_when_pressed=True,
    interval=0.1,
    max_events=1,
)

def show_display(name, font_name):
    # Make the Display Background
    splash = displayio.Group()
    board.DISPLAY.show(splash)
    
    color_bitmap = displayio.Bitmap(160, 128, 1)
    color_palette = displayio.Palette(1)
    color_palette[0] = BACKGROUND_COLOR
    
    bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
    splash.append(bg_sprite)
    
    # Draw a Foreground Rectangle where the name goes
    rect = Rect(0, 50, 160, 70, fill=FOREGROUND_COLOR)
    splash.append(rect)
    
    hello = "HELLO"
    my_name_is = "MY NAME IS"
    
    # Load the Hello font
    large_font_file = "/fonts/Verdana-Bold-18.bdf"
    large_font = bitmap_font.load_font(large_font_file)
    large_font.load_glyphs(hello.encode("utf-8"))
    
    # Load the "My Name Is" font
    small_font_file = "/fonts/Arial-12.bdf"
    small_font = bitmap_font.load_font(small_font_file)
    small_font.load_glyphs(my_name_is.encode("utf-8"))
    
    # Load the Name font
    font_direction='LTR'
    if font_name=="Hebrew" or font_name=="Arabic":
        font_direction='RTL'
    name_font_file = "/fonts/"+font_name+"-18.bdf"
    name_font = bitmap_font.load_font(name_font_file)
    name_font.load_glyphs(name.encode("utf-8"))
    
    # Setup and Center the Hello Label
    splash.append(
        Label(
            large_font,
            anchor_point=(0.5, 0.5),
            anchored_position=(board.DISPLAY.width / 2, 15),
            text=hello,
            color=BACKGROUND_TEXT_COLOR
        )
    )
    
    # Setup and Center the "My Name Is" Label
    splash.append(
        Label(
            small_font,
            anchor_point=(0.5, 0.5),
            anchored_position=(board.DISPLAY.width / 2, 35),
            text=my_name_is,
            color=BACKGROUND_TEXT_COLOR
        )
    )
    
    # Setup and Center the Name Label
    splash.append(
        Label(
            name_font,
            anchor_point=(0.5, 0.5),
            anchored_position=(board.DISPLAY.width / 2, 85),
            text=name,
            color=FOREGROUND_TEXT_COLOR,
            label_direction=font_direction
        )
    )

show_display(NAME_STRINGS[0], FONT_NAMES[0])

# Remap the calculated rotation to 0 - 255
def remap(vector):
    return int(((255 * vector + 85) * 0.75) + 0.5)


# Calculate the Hue rotation starting with Red as 0 degrees
def rotate(degrees):
    cosA = cos(radians(degrees))
    sinA = sin(radians(degrees))
    red = cosA + (1.0 - cosA) / 3.0
    green = 1.0 / 3.0 * (1.0 - cosA) + sqrt(1.0 / 3.0) * sinA
    blue = 1.0 / 3.0 * (1.0 - cosA) - sqrt(1.0 / 3.0) * sinA
    return (remap(red), remap(green), remap(blue))


palette = []
pixels = []

# Generate a rainbow palette
for degree in range(0, 360):
    color = rotate(degree)
    palette.append(color[0] << 16 | color[1] << 8 | color[2])

# Create the Pattern
for x in range(0, NEOPIXEL_COUNT):
    pixels.append(x * 360 // NEOPIXEL_COUNT)


# Main Loop
name_index = 0
last_read = 0
while True:
    for color in range(0, 360, settings["speed"]):
        for index in range(0, NEOPIXEL_COUNT):
            palette_index = pixels[index] + color * settings["direction"]
            if palette_index >= 360:
                palette_index -= 360
            elif palette_index < 0:
                palette_index += 360
            neopixels[index] = palette[palette_index]
        neopixels.show()
        neopixels.brightness = settings["brightness"]
        pad.events.get_into(event)
        if not event:
            continue
        if not event.pressed:
            last_event = None
            continue
        if not last_event:
            if event.key_number == BUTTON_RIGHT:
                settings["direction"] = -1
            elif event.key_number == BUTTON_LEFT:
                settings["direction"] = 1
            elif (event.key_number == BUTTON_UP) and settings["speed"] < 10:
                settings["speed"] += 1
            elif (event.key_number == BUTTON_DOWN) and settings["speed"] > 1:
                settings["speed"] -= 1
            elif (event.key_number == BUTTON_A) and settings["brightness"] < 0.5:
                settings["brightness"] += 0.025
            elif (event.key_number == BUTTON_B) and settings["brightness"] > 0.025:
                settings["brightness"] -= 0.025
            elif (event.key_number == BUTTON_SEL):
                show_display(NAME_STRINGS[0], FONT_NAMES[0])
            elif (event.key_number == BUTTON_START):
                name_index = (name_index + 1) % len(FONT_NAMES)
                show_display(NAME_STRINGS[name_index], FONT_NAMES[name_index])
            last_event = event
