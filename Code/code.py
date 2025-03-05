
#imports
import time
import board
from analogio import AnalogIn
import busio
import simpleio
import adafruit_vl53l4cd
import adafruit_tca9548a
import adafruit_midi
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn
from adafruit_midi.program_change import ProgramChange
from adafruit_midi.control_change import ControlChange

#access pin A5 and A2 on M4 express
analog_in = AnalogIn(board.A5)

#finds voltage at pin x
def get_voltage(pin):
    return (pin.value * 3.3) / 65536



#accuracy of debouncer - more accurate, less speed
    #length of list used to calculate std deviation
debouncer_len = 2


    #  height cutoff for tof sensors in cm
    #  adjust depending on the height of your ceiling/performance area
flight_height = 40


    # use std dev? True or False
stdd = True
    # max value of std dev inside the debouncer lists
stddev = 0.5

    #create I2C bus
i2c = board.I2C()  # uses board.SCL and board.SDA
    # i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller

    # Create the TCA9548A object and give it the I2C bus
tca = adafruit_tca9548a.TCA9548A(i2c)

    #  setup time of flight sensors to use TCA9548A inputs
tof_0 = adafruit_vl53l4cd.VL53L4CD(tca[0])
tof_1 = adafruit_vl53l4cd.VL53L4CD(tca[1])
tof_2 = adafruit_vl53l4cd.VL53L4CD(tca[2])
tof_3 = adafruit_vl53l4cd.VL53L4CD(tca[3])
tof_4 = adafruit_vl53l4cd.VL53L4CD(tca[4])
tof_5 = adafruit_vl53l4cd.VL53L4CD(tca[5])
tof_6 = adafruit_vl53l4cd.VL53L4CD(tca[6])
tof_7 = adafruit_vl53l4cd.VL53L4CD(tca[7])

    #  array of tof sensors
flights = [tof_0, tof_1, tof_2, tof_3, tof_4, tof_5, tof_6,tof_7]#, ]

    #  setup each tof sensor
for flight in flights:
    flight.inter_measurement = 0
    flight.timing_budget = 10  #minimum of 10
    flight.start_ranging()

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




#  state of each tof sensor
#  tracks if you have hit the laser range
pluck_0 = False
pluck_1 = False
pluck_2 = False
pluck_3 = False
pluck_4 = False
pluck_5 = False
pluck_6 = False
pluck_7 = False

        #  array of tof sensor states
plucks = [pluck_0, pluck_1, pluck_2, pluck_3, pluck_4, pluck_5, pluck_6, pluck_7]



datalist_0 = []
datalist_1 = []
datalist_2 = []
datalist_3 = []
datalist_4 = []
datalist_5 = []
datalist_6 = []
datalist_7 = []


    #array of datalists for debouncer
datalist = [datalist_0,datalist_1,datalist_2,datalist_3,datalist_4,datalist_5,datalist_6,datalist_7]

#state of the std deviation calculator
stddev_0 = False
stddev_1 = False
stddev_2 = False
stddev_3 = False
stddev_4 = False
stddev_5 = False
stddev_6 = False
stddev_7 = False
#array of stddevs
stddevs = [stddev_0, stddev_1, stddev_2, stddev_3, stddev_4, stddev_5, stddev_6, stddev_7]



val = flight_height

#makes lists for debouncers of appropriate length
for j in range(len(datalist)):
        for i in range(debouncer_len):
            datalist[j].insert(0,val)
        #print(datalist)




#sets midi notes for the different modes
low_notes = [48, 50, 52, 53, 55, 57, 59, 60]  #preset = [48, 52, 55, 59, 60, 64, 67, 71]
high_notes = [60, 62, 64, 65, 67, 69, 71, 72]
notes = [48, 50, 52, 53, 55, 57, 59, 60]


volt = get_voltage(analog_in)
#main loop
while True:
    #detect if switch is on or off
    volt = get_voltage(analog_in)


    #if the switch is on...
    if volt >= 3.2:

        print("if switch mode 1")

        #makes it so that the midi will only communicate with one channel at a time
        #midi.send(ControlChange(124,0))

        volumes = []

        coeff = 100/flight_height



        for i in range(flight_height):
            volumes.append(int(27+i*coeff))



    #while the switch is on...
    while volt >= 3.2:
        #loops through the 8 different sensors
        for f in range(7):


            #creates a new midi channel for each sensor, that way, when they modulate, each note is changed
            #without this, the volume accross all notes is modulated - sounds disgusting
            midi_in_channel = f+2
            midi_out_channel = f+2
            #  midi setup
            #  UART is setup as the input
            midi = adafruit_midi.MIDI(
            midi_in=uart,
            midi_out=uart,
            in_channel=(midi_in_channel - 1),
            out_channel=(midi_out_channel - 1),
            debug=False,

            )

            #resets the note sound
            midi.send(ProgramChange(80))

            while not flights[f].data_ready:
                pass
            #  reset tof sensors
            #  reset tof sensors
            #  reset tof sensors
            #  reset tof sensors
            flights[f].clear_interrupt()
            #  if the reading from a tof is not 0...
            if flights[f].distance != 0.0:

                #  map range of tof sensor distance to midi parameters
                #  modulation
                mod = round(simpleio.map_range(flights[f].distance, 0, 100, 120, 0))
                #  sustain
                sus = round(simpleio.map_range(flights[f].distance, 0, 100, 127, 0))
                #  velocity
                vel = 120 #round(simpleio.map_range(flights[f].distance, 0, 150, 120, 0))
                modulation = int(mod)
                sustain = int(sus)
                #  create sustain and modulation CC message
                pedal = ControlChange(71, sustain)
                modWheel = ControlChange(1, modulation)
                #  send the sustain and modulation messages
                midi.send([modWheel, pedal])
                #removes the last datapoint from the list to prepare for the next datapoint
                datalist[f].remove(datalist[f][debouncer_len-1])

                #adds distance to the list
                datalist[f].insert(0,int(flights[f].distance))


                #calculate std deviation, brute force method
                mean = sum(datalist[f]) / len(datalist[f])
                variance = sum([((x - mean) ** 2) for x in datalist[f]]) / len(datalist[f])
                calc_stddev = variance ** 0.5

                #uses calculated std dev to add a secondary componenet to debouncer
                #debouncer both checks for consistent values below a threshold, aka flight_height, and also for the proximity of those values to each other
                #if a sensor is particularly noisy, it will still output values below 30, but rarely consistent values below 30 if it is truly just noise
                if calc_stddev > stddev:
                    stddevs[f] = False
                else:
                    stddevs[f] = True

                if not stdd:
                    if plucks[f]:
                        stddevs[f] = False
                    else:
                        stddevs[f] = True


                #  if tof registers a height lower than the set max height...
                if all(j < flight_height for j in datalist[f]) and stddevs[f] and not plucks[f]:
                    #  set state tracker
                    plucks[f] = True


                    #  convert tof distance to a velocity value
                    velocity = int(vel)

                    #  send midi note with velocity and sustain message
                    midi.send([NoteOn(notes[f], velocity),pedal])


                #converts distace away from seonsor into volume modulation
                if plucks[f] == True:
                    dist = int(datalist[f][1]) -1
                    if dist > 0 and dist < flight_height - 1:
                        vol = volumes[-dist]

                        #modulates volume
                        midi.send(ControlChange(7,vol))


                #  if tof registers a height = to or greater than set max height
                #  aka you remove your hand from above the sensor...
                if any(j >= flight_height for j in datalist[f]) and plucks[f] and not stddevs[f]:
                    #  reset state
                    plucks[f] = False

                    #  send midi note off
                    midi.send(NoteOff(notes[f], velocity))

        #gets voltage for the switch check
        volt = get_voltage(analog_in)

        #turns all notes off, regardless of state
    midi.send(ControlChange(120,0))
    #if switch gets flipped off...
    if volt < 3.2:
        print("if switch mode 2")

        #swtiches back so midi will communicate in all channels
        midi.send(ControlChange(125,0))

        #brings volume back up after the volume modulation in the previous loop
        midi.send(ControlChange(7,120))

    #while the swtich is off...
    while volt < 3.2:
        #loops through the 8 tof sensors
        for f in range(7):
            while not flights[f].data_ready:
                pass
            #  reset tof sensors
            #  reset tof sensors
            #  reset tof sensors
            #  reset tof sensors
            flights[f].clear_interrupt()
            #  if the reading from a tof is not 0...
            if flights[f].distance != 0.0:
                #  map range of tof sensor distance to midi parameters
                #  modulation
                mod = round(simpleio.map_range(flights[f].distance, 0, 100, 120, 0))
                #  sustain
                sus = round(simpleio.map_range(flights[f].distance, 0, 100, 127, 0))
                #  velocity
                vel = 120 #round(simpleio.map_range(flights[f].distance, 0, 150, 120, 0))
                modulation = int(mod)
                sustain = int(sus)
                #  create sustain and modulation CC message
                pedal = ControlChange(71, sustain)
                modWheel = ControlChange(1, modulation)
                #  send the sustain and modulation messages
                midi.send([modWheel, pedal])
                #removes last datapoint in list
                datalist[f].remove(datalist[f][debouncer_len-1])

                #adds distance to the list
                datalist[f].insert(0,int(flights[f].distance))



                #calculate std deviation, brute force method
                mean = sum(datalist[f]) / len(datalist[f])
                variance = sum([((x - mean) ** 2) for x in datalist[f]]) / len(datalist[f])
                calc_stddev = variance ** 0.5

                #uses calculated std dev to add a secondary componenet to debouncer
                #debouncer both checks for consistent values below a threshold, aka flight_height, and also for the proximity of those values to each other
                #if a sensor is particularly noisy, it will still output values below 30, but rarely consistent values below 30 if it is truly just noise
                if calc_stddev > stddev:
                    stddevs[f] = False
                else:
                    stddevs[f] = True

                if not stdd:
                    if plucks[f]:
                        stddevs[f] = False
                    else:
                        stddevs[f] = True



                #  if tof registers a height lower than the set max height...
                while all(j < flight_height for j in datalist[f]) and stddevs[f] and not plucks[f]:

                    if int(flights[f].distance) < .5*flight_height:  #if hand is lower than halfway to flight height


                        bass = ProgramChange(81)
                        vel = 120 #round(simpleio.map_range(flights[f].distance, 0, 30, 127, 75))

                        velocity = int(vel)
                        #  send midi message
                        midi.send([bass, NoteOn(low_notes[f], velocity)])

                        plucks[f] = True



                    if (int(flights[f].distance) >= .5*flight_height):   # if hand is higher than halfway to flight height

                        lead = ProgramChange(54)
                        vel = 120 #round(simpleio.map_range(flights[f].distance, 30, flight_height, 127, 75))

                        velocity = int(vel)
                        #  send midi message
                        midi.send([lead, NoteOn(high_notes[f], velocity)])

                        plucks[f] = True




                        #turns off low note if it was playing
                #  send note off message
                #  if tof registers a height = to or greater than set max height
                #  aka you remove your hand from above the sensor...
                if any(j >= flight_height for j in datalist[f]) and plucks[f] and not stddevs[f]:
                    #  reset state
                    plucks[f] = False
                    #check which sensors are pinging
                    #print(f, plucks[f])

                    #print(velocity)
                    #  send midi note off
                    #if check != 0:
                    midi.send(NoteOff(low_notes[f], velocity))

                    #if checker != 0:
                    midi.send(NoteOff(high_notes[f], velocity))
        volt = get_voltage(analog_in)

        #turns off all notes, failsafe
    midi.send(ControlChange(120,0))
    '''e = 3

    if e == 3:
        print("If switch mode 3")

        mods = []

        for i in range(0,4,1):
            mods.append(i*16+50)

        for j in range(4,0,-1):
            mods.append(j*16+50)
        #print(mods)
        s = 0


    while e == 3:
        #loops through the 8 different sensors
        for f in range(7):


            #creates a new midi channel for each sensor, that way, when they modulate, each note is changed
            #without this, the volume accross all notes is modulated - sounds disgusting
            midi_in_channel = f+2
            midi_out_channel = f+2
            #  midi setup
            #  UART is setup as the input
            midi = adafruit_midi.MIDI(
            midi_in=uart,
            midi_out=uart,
            in_channel=(midi_in_channel - 1),
            out_channel=(midi_out_channel - 1),
            debug=False,

            )

            #resets the note sound
            midi.send(ProgramChange(80))

            while not flights[f].data_ready:
                pass
            #  reset tof sensors
            #  reset tof sensors
            #  reset tof sensors
            #  reset tof sensors
            flights[f].clear_interrupt()
            #  if the reading from a tof is not 0...
            if flights[f].distance != 0.0:

                #  map range of tof sensor distance to midi parameters
                #  modulation
                mod = round(simpleio.map_range(flights[f].distance, 0, 100, 120, 0))
                #  sustain
                sus = round(simpleio.map_range(flights[f].distance, 0, 100, 127, 0))
                #  velocity
                vel = 120 #round(simpleio.map_range(flights[f].distance, 0, 150, 120, 0))
                modulation = int(mod)
                sustain = int(sus)
                #  create sustain and modulation CC message
                pedal = ControlChange(71, sustain)
                modWheel = ControlChange(1, modulation)
                #  send the sustain and modulation messages
                midi.send([modWheel, pedal])
                #removes the last datapoint from the list to prepare for the next datapoint
                datalist[f].remove(datalist[f][debouncer_len-1])

                #adds distance to the list
                datalist[f].insert(0,int(flights[f].distance))


                #calculate std deviation, brute force method
                mean = sum(datalist[f]) / len(datalist[f])
                variance = sum([((x - mean) ** 2) for x in datalist[f]]) / len(datalist[f])
                calc_stddev = variance ** 0.5

                #uses calculated std dev to add a secondary componenet to debouncer
                #debouncer both checks for consistent values below a threshold, aka flight_height, and also for the proximity of those values to each other
                #if a sensor is particularly noisy, it will still output values below 30, but rarely consistent values below 30 if it is truly just noise
                if calc_stddev > stddev:
                    stddevs[f] = False
                else:
                    stddevs[f] = True

                if not stdd:
                    if plucks[f]:
                        stddevs[f] = False
                    else:
                        stddevs[f] = True


                #  if tof registers a height lower than the set max height...
                if all(j < flight_height for j in datalist[f]) and stddevs[f] and not plucks[f]:
                    #  set state tracker
                    plucks[f] = True


                    #  convert tof distance to a velocity value
                    velocity = int(vel)

                    #  send midi note with velocity and sustain message
                    midi.send([NoteOn(notes[f], velocity),pedal])


                #converts distace away from seonsor into volume modulation
                if plucks[f] == True:
                    dist = int(datalist[f][1]) -1

                    if dist > 0 and dist < flight_height - 1:

                        vol = mods[s]
                        s += 1
                        time.sleep(dist*.0025)

                        if s == 8:
                            s = 0

                        #modulates volume
                        midi.send(ControlChange(7,vol))


                #  if tof registers a height = to or greater than set max height
                #  aka you remove your hand from above the sensor...
                if any(j >= flight_height for j in datalist[f]) and plucks[f] and not stddevs[f]:
                    #  reset state
                    plucks[f] = False

                    #  send midi note off
                    midi.send(NoteOff(notes[f], velocity))

        #gets voltage for the switch check
        e = mode_selector()'''


        #turns all notes off, regardless of state
    midi.send(ControlChange(120,0))
    #if switch gets flipped off...





