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

class NoGps(gps.Gps, threading.Thread):
   def __init__(self, db):
      threading.Thread.__init__(self)
      gps.Gps.__init__(self, db)
      self.debug = self.db.Get("config/misc/debug")
      print "nmea> debug = %d" % self.debug
      self.running = 0

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
      print "nogps> running"

      valid = 1
      latdeg = 30
      latmin = 34.129
      londeg = -96
      lonmin = 16.996
      alt = 300.0

      self.db.Get("gps/vector").speed_kn = 0
      self.db.Get("gps/vector").course = 0
      self.db.Get("gps/pos/here").SetPos((latdeg, latmin), (londeg, lonmin))
      self.db.Get("gps/pos/here").alt_f = alt
      self.db.Put("gps/sat/tracking", 0)
      self.db.Put("gps/sat/visible", 0)
      self.db.Put("gps/mode", 3)
      self.db.Put("gps/dop", 2.5)
      self.db.Put("gps/pos/valid", valid)

      while self.running:
         if valid:
            (year,month,day,hour,minute,second,junk,junk,junk) = time.gmtime()
            self.db.Put("gps/time/valid", valid)

            self.db.Put("gps/time/hour", hour)
            self.db.Put("gps/time/minute", minute)
            self.db.Put("gps/time/second", second)
            self.db.Put("gps/time/month", month)
            self.db.Put("gps/time/day", day)
            self.db.Put("gps/time/year", year)


         if self.debug and valid:
            print "nmea> GPRMC time %02d/%02d/%02d %02d:%02d:%02d UTC"  % (month, day, year, hour, minute, second)
            print "nmea> GPRMC lat %4ddeg %2.3fmin" % (latdeg, latmin)
            print "nmea> GPRMC lon %4ddeg %2.3fmin" % (londeg, lonmin)
            print "nmea> GPRMC speed %3.1f crs %3.1f (%s)"  % (speed, course, units.CompassOrd2(course))
            print "nmea> GPGGA alt: %4.1fft" % (tracking, units.m2f(alt))

         time.sleep(.6)
      print "nmea> exiting..."
