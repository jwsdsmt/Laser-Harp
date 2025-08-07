#imports
import time
import board
import busio
import adafruit_vl53l4cd
import adafruit_tca9548a
import adafruit_midi
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn
from adafruit_midi.program_change import ProgramChange
from adafruit_midi.control_change import ControlChange

OFF = 0
LOW = 1
HIGH = 2

def map_scale(val, min1, max1, min2, max2):
    return min(max(val - min1, 0) / (max1 - min1), 1) * (max2 - min2) + min2
    
#  height cutoff for tof sensors in cm
#  adjust depending on the height of your ceiling/performance area
flight_height = 10

i2c = board.I2C()
tca = adafruit_tca9548a.TCA9548A(i2c)

flights = [None] * len(tca)
keystate = [OFF] * len(tca)
flight_heights = [flight_height] * len(tca)

for i in range(len(tca)):
    flights[i] = adafruit_vl53l4cd.VL53L4CD(tca[len(tca) - i - 1])
    flights[i].inter_measurement = 50
    flights[i].timing_budget = 10
    flights[i].start_ranging()

#  midi uart setup for music maker featherwing - baudrate should stay at 31250, otherwise MIDI will no longer communicate
uart = busio.UART(board.TX, board.RX, baudrate=31250)

midi_in_channel = 1
midi_out_channel = 1

#  midi setup
#  UART is setup as the input
midi = adafruit_midi.MIDI(
    midi_in=uart,
    midi_out=uart,
    in_channel=(midi_in_channel - 1),
    out_channel=(midi_out_channel - 1),
    debug=False,
)

#sets midi notes for the different modes
low_notes = [48, 50, 52, 53, 55, 57, 59, 60]
high_notes = [60, 62, 64, 65, 67, 69, 71, 72]

midi.send(ControlChange(121, 0))
midi.send(ProgramChange(23))
program = 0

previous_time = time.monotonic()
current_time = time.monotonic()
frequency = 100
timestep = 1 / frequency

while True:
    current_time = time.monotonic()
    if current_time < previous_time + timestep:
        continue
    previous_time = current_time

    for i in range(len(flights)):
        if not flights[i].data_ready:
            pass
        flights[i].clear_interrupt()
        distance = flights[i].distance
        flight_heights[i] = flight_heights[i] * 0.999 + distance * 0.001

        current_state = OFF
        if distance < flight_heights[i] * 5/8:
            current_state = LOW
        
        if current_state != keystate[i]:
            keystate[i] = current_state
            if current_state == OFF:
                midi.send(NoteOff(low_notes[i]))
            if current_state == LOW:
                midi.send(NoteOn(low_notes[i]))