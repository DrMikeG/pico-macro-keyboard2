# Adding Rugged fingerprint reader - can I make it blink?

import time
import board
import busio

from digitalio import DigitalInOut, Direction

from pmk import PMK
#from pmk.platform.keybow2040 import Keybow2040 as Hardware          # for Keybow 2040
from pmk.platform.rgbkeypadbase import RGBKeypadBase as Hardware  # for Pico RGB Keypad Base

import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

import adafruit_fingerprint

led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT
uart = busio.UART(tx=board.GP8, rx=board.GP9, baudrate=57600)
finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

# Set up Keybow
keybow = PMK(Hardware())
keys = keybow.keys

# Set up the keyboard and layout
keyboard = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(keyboard)


# pylint: disable=too-many-statements
def enroll_finger(location):
    """Take a 2 finger images and template it, then store in 'location'"""
    for fingerimg in range(1, 3):
        if fingerimg == 1:
            print("Place finger on sensor...")
        else:
            print("Place same finger again...")

        while True:
            i = finger.get_image()
            if i == adafruit_fingerprint.OK:
                print("Image taken")
                break
            if i == adafruit_fingerprint.NOFINGER:
                print(".")
            elif i == adafruit_fingerprint.IMAGEFAIL:
                print("Imaging error")
                return False
            else:
                print("Other error")
                return False

        print("Templating...")
        i = finger.image_2_tz(fingerimg)
        if i == adafruit_fingerprint.OK:
            print("Templated")
        else:
            if i == adafruit_fingerprint.IMAGEMESS:
                print("Image too messy")
            elif i == adafruit_fingerprint.FEATUREFAIL:
                print("Could not identify features")
            elif i == adafruit_fingerprint.INVALIDIMAGE:
                print("Image invalid")
            else:
                print("Other error")
            return False

        if fingerimg == 1:
            print("Remove finger")
            time.sleep(1)
            while i != adafruit_fingerprint.NOFINGER:
                i = finger.get_image()

    print("Creating model...")
    i = finger.create_model()
    if i == adafruit_fingerprint.OK:
        print("Created")
    else:
        if i == adafruit_fingerprint.ENROLLMISMATCH:
            print("Prints did not match")
        else:
            print("Other error")
        return False

    print("Storing model #%d..." % location)
    i = finger.store_model(location)
    if i == adafruit_fingerprint.OK:
        print("Stored")
    else:
        if i == adafruit_fingerprint.BADLOCATION:
            print("Bad storage location")
        elif i == adafruit_fingerprint.FLASHERR:
            print("Flash storage error")
        else:
            print("Other error")
        return False

    return True




def get_fingerprint():
    """Get a finger print image, template it, and see if it matches!"""
    print("Waiting for image...")
    while finger.get_image() != adafruit_fingerprint.OK:
        pass
    print("Templating...")
    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
        return False
    print("Searching...")
    if finger.finger_search() != adafruit_fingerprint.OK:
        return False
    return True

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
colour = (0, 0, noZero)

locked_colour = (noZero, 0, 0)


# Set the LEDs for each key in the current layer
for k in layer.keys():
    keys[k].set_led(*colour)

# To prevent the strings (as opposed to single key presses) that are sent from
# refiring on a single key press, the debounce time for the strings has to be
# longer.
long_debounce = 0.25
fired = False
lockout_time = 30.0

locked = True
time_of_last_unlock = 0

finger.set_led(color=1, mode=1)

while True:
    # Always remember to call keybow.update()!
    keybow.update()

    if locked:
        for k in layer.keys():
            keys[k].set_led(*locked_colour)
        finger.set_led(color=1, mode=3)

        #enroll_finger(1)

        if get_fingerprint():
            print("Detected #", finger.finger_id, "with confidence", finger.confidence)
            locked = False
            time_of_last_unlock = time.monotonic()

    else:
        for k in layer.keys():
            keys[k].set_led(*colour)
        finger.set_led(color=2, mode=3)

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

        if time.monotonic() - time_of_last_unlock > lockout_time:
            locked = True