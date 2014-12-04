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

import aprs, db, time, tcpconsole, tnc, display, router, aprsscr, gpsscr, config, configscr, mapscr, mesgscr

thedb = db.Db()
theConfig = config.Config(thedb)
theConfig.Load()

debug = thedb.Get("config/misc/debug")

#physical devices

if thedb.Get("config/gps/enable"):
   gpstype = thedb.Get("config/gps/type")
   if gpstype == "m12":
      #M12 gps
      import m12
      thegps = m12.M12(thedb.Get("config/gps/port"), thedb)
      thegps.Start()
   elif gpstype == "nmea":
      #NMEA gps
      import nmea
      thegps = nmea.Nmea(thedb.Get("config/gps/port"), thedb)
      thegps.Start()
   elif gpstype == "nogps":
      #static GPS location - useful for testing w/o a connected gps
      #pulls time from system clock
      import nogps
      thegps = nogps.NoGps(thedb)
      thegps.Start()
   elif debug:
      print "xlaprs> not a known gps type"


#TNC
theKISS = tnc.Kiss(thedb.Get("config/tnc/port"), thedb)
theKISS.Start()

if thedb.Get("config/display/enable"):
   #GLC
   theGlc = display.Glc(thedb.Get("config/display/port"), thedb)
   theGlc.Start()
   thedb.Put("global/display", theGlc)

   screens = [gpsscr.GPSScreen(thedb),
              aprsscr.APRSScreen(thedb),
              aprsscr.APRSDetailScreen(thedb),
              mesgscr.MesgScreen(thedb),
#              mapscr.MapScreen(thedb),
              configscr.ConfigScreen(thedb)]
   thedb.Put("global/screenlist", screens)

   theRouter = router.Router(thedb)
   theRouter.Start()

theAprs = aprs.Aprs(theKISS, thedb)
theAprs.Start()

theAprsCalc = aprs.AprsCalc(thedb)
theAprsCalc.Start()

thetcpconsole = tcpconsole.Tcpconsole(24242, thedb)
thetcpconsole.Start()

try:
   while 1:
      if debug: print "xlaprs> tick"
      time.sleep(5)

except KeyboardInterrupt:
   print "xlaprs> exiting..."

   thetcpconsole.Stop()
   theAprsCalc.Stop()
   theAprs.Stop()
   if thedb.Get("config/display/enable"):
      theRouter.Stop()
      time.sleep(1.5)
      theGlc.Stop()
   else:
      time.sleep(1.5)
   
   theKISS.Stop()
   if thedb.Get("config/gps/enable"):
      thegps.Stop()
   time.sleep(1.5)
   theConfig.Save()
