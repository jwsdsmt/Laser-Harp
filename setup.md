# Setting Up the Device

This document assumes you have already correctly fabricated and assembled the laser harp.

This device uses CircuitPython, a variant of MicroPython maintained by Adafruit, which runs on their boards.

The circuitpy directory contains all the code you need to get the device working, written for CircuitPython 9.x.
Install CircuitPython 9.x on your Adafruit Feather RP2040, then copy code.py and the lib folder from this project to the CIRCUITPY drive of the board.
If you are using a different version of CircuitPython, download the official CircuitPython bundle for that version, and check to make sure all the libraries this project uses are available.
Then, replace the modules contained in the lib folder with those compiled for your version of CircuitPython, obtained from the bundle.

The code.py file should never need to be modified, because the device is self calibrating.
Unless a newer version of the libraries or CircuitPython introduce breaking changes, you should be good to go.
