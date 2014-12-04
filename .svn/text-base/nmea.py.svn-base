#!/usr/bin/python
#--------------------------------------------------------------------------
# Copyright 2003 William Orton - will@loopfree.net
#                Kevin Glueck  - kglueck@viz.tamu.edu
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. The license and distribution terms for any publically available version
#    or derivative of this code cannot be changed.  i.e. this code cannot 
#    simply be copied and put under another distribution license
#    [including, but not limited to, the GNU Public License.]
#
# THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL
# THE AUTHOR OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# --------------------------------------------------------------------------

import gps, serial, threading, time, string, units, waypoint, vector

class Nmea(gps.Gps, threading.Thread):
   def __init__(self, port, db):
      threading.Thread.__init__(self)
      gps.Gps.__init__(self, db)
      self.debug = self.db.Get("config/misc/debug")
      print "nmea> debug = %d" % self.debug
      self.port = port
      self.running = 0
      try:
         self.s = serial.Serial(port, 4800, rtscts=0, xonxoff=0, timeout=0)
      except:
         print "nmea> could not open serial port %d" % self.port

      self.status = "initted"

   def Start(self):
      if self.running: return
      self.running = 1
      threading.Thread.start(self)
      self.status = "running"

   def Stop(self):
      if not self.running: return
      self.running = 0
      threading.Thread.join(self, 5)
      self.status = "stopped"

   def run(self):
      print "nmea> running"
      data = ""

      self.Reset()

      while self.running:
         data = data + self.s.read(500)
         data = data.replace("\r\n", "")
         if string.find(data, "$") >= 0:
            # find beginning of NMEA sentence, drop any characters preceding first $
            # (they are assumed to be garbage)
            data = data[string.find(data, "$") + 1:]
            # split data into array of individual NMEA sentences, add $ back to each line
            lines = ["$" + x for x in data.split("$")]
            # if we have data in lines & length last line <= 3 char
            # or the last part of last line doesn't include checksum,
            # we want to put the unfinished sentence back so that the
            # next read will (hopefully) finish it...
            if len(lines) > 0 and (len(lines[-1]) <= 3 or lines[-1][-3] != "*"):
               data = lines.pop()
            else:  # else we clear the way for new data to be read next time
               data = ""
            for line in lines:
               # compare the computed/given cksums, if good, send on to parser
               if Xsum(line) == line[-2:]:
                  try:
                     self.Parse(line[:-3])
                  except IndexError:
                     if self.debug: print "nmea> bad sentence data"
               else:
                  if self.debug: print "nmea> bad xsum %s" % line
                
         time.sleep(.2)
      print "nmea> exiting..."
      self.s.close()

   def Reset(self):
      self.prnSig = {}
      self.prnEl = {}
      self.prnAz = {}

   def Seteas(self):
      """Combine self.prn* into dict for db"""
      eas = {}
      for prn in self.prnAz.keys():
         if prn in self.prnEl and prn in self.prnSig:
            eas[prn] = {"el":self.prnEl[prn], "az":self.prnAz[prn], "sig":self.prnSig[prn]}
      self.db.Put("gps/sat/prn/eas", eas)

   def Parse(self, line):
      if line[1:6] == "GPRMC":
         #$GPRMC,072028,A,3516.325,N,12039.739,W,000.0,351.1,130302,014.5,E
         #time,A=OK/V=warn,lat,N/S,lon,E/W,speed,course,DDMMYY,mag-var,E/W
         # should have 12 commas
         if self.debug: print "nmea> parse GPRMC: %s" % line

         if string.count(line, ",") > 11 :
           toks = string.split(line, ",")
           if toks[2] == "A":
              valid = 1
           else:
              valid = 0
           self.db.Put("gps/pos/valid", valid)
           self.db.Put("gps/time/valid", valid)
           if valid:
              hour =   getint(toks[1][0:2])
              minute = getint(toks[1][2:4])
              second = getint(toks[1][4:6])

              latdeg = getint(toks[3][0:2])
              latmin = getfloat(toks[3][2:8])
              if toks[4] == "S": latdeg = -latdeg

              londeg = getint(toks[5][0:3])
              lonmin = getfloat(toks[5][3:9])
              if toks[6] == "W": londeg = -londeg

              speed = getfloat(toks[7])  # nmea gives in knots (nm)
              course = getfloat(toks[8])

              day   = getint(toks[9][0:2])
              month = getint(toks[9][2:4])
              year  = getint(toks[9][4:6])

              # do we want to use this somewhere?  magnetic variance
              #magvar = getfloat(toks[10])
              #if toks[11] == "W": magvar = -magvar
              #self.db.Put("gps/mag", magvar)

              self.db.Put("gps/time/hour", hour)
              self.db.Put("gps/time/minute", minute)
              self.db.Put("gps/time/second", second)
              self.db.Put("gps/time/month", month)
              self.db.Put("gps/time/day", day)
              self.db.Put("gps/time/year", year)

              self.db.Get("gps/vector").speed_kn = speed
              self.db.Get("gps/vector").course = course

              self.db.Get("gps/pos/here").SetPos((latdeg, latmin), (londeg, lonmin))

           if self.debug:
              if valid: v = "valid"
              else: v = "invalid"
              print "nmea> GPRMC %s" % v

           if self.debug and valid:
              print "nmea> GPRMC time %02d/%02d/%02d %02d:%02d:%02d UTC"  % (month, day, year, hour, minute, second)
              print "nmea> GPRMC lat %4ddeg %2.3fmin" % (latdeg, latmin)
              print "nmea> GPRMC lon %4ddeg %2.3fmin" % (londeg, lonmin)
              print "nmea> GPRMC speed %3.1f crs %3.1f (%s)"  % (speed, course, units.CompassOrd2(course))
              #print "nmea> GPRMS magvar %2.1f" % magvar

      elif line[1:6] == "GPGGA":
         #$GPGGA,141049.87,3409.5207,N,09704.3370,W,1,05,1.9,00269,M,,,,
         #time,lat,N/S,lon,E/W,quality,numsat,horzPrecision,alt,M,geoid sep,
         #  age of diff gps data,diff ref station
         #  (quality = 0: fix not avail/invalid, 1: GPS fix, 2: Diff GPS fix)
         # should have 14 commas
         if self.debug: print "nmea> parse GPGGA: %s" % line
         #if string.count(line, ",") > 13 :
         if self.db.Get("gps/pos/valid"):
           toks = string.split(line, ",")
           tracking = getint(toks[7])
           alt = getfloat(toks[9])

           self.db.Put("gps/sat/tracking", tracking)
           self.db.Get("gps/pos/here").alt_m = alt

           if self.debug:
              print "nmea> GPGGA tracking %d sats alt: %4.1fft" % (tracking, units.m2f(alt))

      elif line[1:6] == "GPGSV":
         #$GPGSV,3,2,09,26,08,321,00,27,70,131,42,28,47,312,40,29,20,306,43*7C
         #tot#,this#,inView,PRN,el,az,sig,PRN,el,az,sig,PRN,el,az,sig,PRN,
         # el,az,sig
         # should have 7, 11, 15, or 19 commas, depending on how many satellites included
         if self.debug: print "nmea> parse GPGSV: %s" % line
         #if string.count(line, ",") > 6 :
         if self.db.Get("gps/pos/valid"):
           toks = string.split(line, ",")
         
           total = getint(toks[1])
           this = getint(toks[2])
           visible = getint(toks[3])

           for t in range(4, string.count(line, ","), 4):
              if len(toks[t]) > 0:
                 prn = getint(toks[t])
                 self.prnEl[prn] = getint(toks[t+1])
                 self.prnAz[prn] = getint(toks[t+2])
                 self.prnSig[prn] = getint(toks[t+3])

           # if this is the last sentence in a sequence of GPGSVs
           if this == total:
              self.db.Put("gps/sat/visible", visible)
              self.Seteas()
              self.prnSig = {}
              self.prnEl = {}
              self.prnAz = {}

      elif line[1:6] == "GPGSA":
         #$GPGSA,A,3,07,08,11,13,,27,28,29,31,,,,2.4,1.4,1.9,*32
         #M/Amode,2/3Dmode,PRN# for sat used in calc (null for unused)....,PDOP,HDOP,VDOP
         # should have 17 commas
         if self.debug: print "nmea> parse GPGSA: %s" % line
         toks = string.split(line, ",")

         # this next if protects against a malformed GPGSA sentence
         # fixavail can be 1 = Fix not available
         #                 2 = 2D
         #                 3 = 3D
         mode = getint(toks[2])
         if mode > 1:
            dop = getfloat(toks[15])

            self.db.Put("gps/mode", mode)
            self.db.Put("gps/dop", dop)

            #AFAIK these aren't currently used, but I'm gonna leave 'em be for now. -kglueck
            hdop = getfloat(toks[16])
            vdop = getfloat(toks[17])

            solution = []
            for x in range (3, 15):
               if len(toks[x]) > 0:
                 prn = getint(toks[x])
                 if prn:
                    solution.append(prn)

            self.db.Put("gps/hdop", hdop)
            self.db.Put("gps/vdop", vdop)
            self.db.Put("gps/sat/prn/solution", solution)

#
# unused for now
#
      elif line[1:6] == "GPRMB":
         pass
      elif line[1:6] == "GPBOD":
         pass
      elif line[1:6] == "GPRTE":
         pass
      elif line[1:6] == "GPGLL":
         pass
      elif line[1:6] == "GPVTG":
         pass

#
#garmin-specific
#
      elif line[1:6] == "PGRME":
         pass
      elif line[1:6] == "PGRMZ":
         pass
      elif line[1:6] == "PGRMM":
         # this one is not all that interesting...just the datum being used...
         pass
      else:
         if self.debug: print "nmea> unknown sentence type %s" % line



def Xsum(s):
   sum = 0
   for char in s[1:string.find(s, "*")]: sum ^= ord(char)
   return "%02X" % sum

def getint(s):
   try:
      return int(s)
   except:
      return 0

def getfloat(s):
   try:
      return float(s)
   except:
      return 0.0
