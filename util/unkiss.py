#!/usr/bin/python

# Takes a KPC-3 out of KISS mode
# Reuqires pyserial

import serial, string

FEND = "\xC0"
FESC = "\xDB"
TFEND = "\xDC"
TFESC = "\xDD"
try:
   s = serial.Serial(2, 9600, rtscts=0, xonxoff=0, timeout=0.1)
except:
   print "could not open serial port"
kissframe = FEND + "\xFF" + FEND
s.write(kissframe)
