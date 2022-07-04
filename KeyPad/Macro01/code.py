# SPDX-FileCopyrightText: 2021 Sandy Macdonald
#
# SPDX-License-Identifier: MIT

# An advanced example of how to set up a HID keyboard.

# There are three layers, selected by pressing and holding key 0 (bottom left),
# then tapping one of the coloured layer selector keys above it to switch layer.

# The layer colours are as follows:

#  * layer 1: pink: numpad-style keys, 0-9, delete, and enter.
#  * layer 2: blue: sends strings on each key press
#  * layer 3: media controls, rev, play/pause, fwd on row one, vol. down, mute,
#             vol. up on row two

# You'll need to connect Keybow 2040 to a computer, as you would with a regular
# USB keyboard.

# Drop the `pmk` folder
# into your `lib` folder on your `CIRCUITPY` drive.

# NOTE! Requires the adafruit_hid CircuitPython library also!

import time
from pmk import PMK
#from pmk.platform.keybow2040 import Keybow2040 as Hardware          # for Keybow 2040
from pmk.platform.rgbkeypadbase import RGBKeypadBase as Hardware  # for Pico RGB Keypad Base

import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

# Set up Keybow
keybow = PMK(Hardware())
keys = keybow.keys

# Set up the keyboard and layout
keyboard = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(keyboard)


# in the orientation I'm comfortable the key grid is 
# 03 07 11 15
# 02 06 10 14 
# 01 05 09 13
# 00 04 08 12

#
# Note that keys 0-3 are reserved as the modifier and layer selector keys
# respectively.
layer =     {3: "PKINUM",
               7: "UserName",
               11: "PWD",
               15: "KEYPASS",
               2: "PLM",
               6: "GITKEY"}


# The colours for each layer
noZero = 32
colour = (noZero, 0, noZero)

# Set the LEDs for each key in the current layer
for k in layer.keys():
    keys[k].set_led(*colour)

# To prevent the strings (as opposed to single key presses) that are sent from
# refiring on a single key press, the debounce time for the strings has to be
# longer.
long_debounce = 0.25
fired = False

while True:
    # Always remember to call keybow.update()!
    keybow.update()

    # Loop through all of the keys in the layer and if they're pressed, get the
    # key code from the layer's key map
    for k in layer.keys():
        if keys[k].pressed:
            key_press = layer[k]

            # If the key hasn't just fired (prevents refiring)
            if not fired:
                fired = True
                # Send the right sort of key press and set debounce for each
                layout.write(key_press)

    # If enough time has passed, reset the fired variable
    if fired and time.monotonic() - keybow.time_of_last_press > long_debounce:
        fired = False
