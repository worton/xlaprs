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

import time, screen, waypoint, vector, widget, units

class GPSScreen(screen.Screen):
   def __init__(self, db):
      screen.Screen.__init__(self, db)
      self.id = id

      try:
         import apm
         self.apmenabled = 1
         self.wapm = widget.LabeledValue((53,0), self.disp, "%3d%% %c%2d:%02d", "", (0,' ',0,0))
         self.power = apm.Apm()
      except ImportError:
         self.apmenabled = 0

#left side of screen
#line1      
      self.wspeed  = widget.LabeledValue((0, 15), self.disp, "%05.1f", " m/h", 1.0)
#line2
      self.walt    = widget.LabeledValue((0, 25), self.disp, "%05d", " ft", 1)
      self.wvspeed = widget.LabeledValue((60,25), self.disp, "%+04d", " fpm", 1)
#line3 
      self.wlat    = widget.LabeledValue((0, 35), self.disp, "%s", "", "")
#line4
      self.wlon    = widget.LabeledValue((0, 45), self.disp, "%s", "", "")
#line5 
      self.wclock  = widget.GPSClock((0, 55), self.disp, self.db)

#right side of screen
#line 1 
      self.wcourse  = widget.LabeledValue((130,5), self.disp, "%s", "", "NNE")
#line 2
      self.wcourse2 = widget.LabeledValue((130,15), self.disp, "%05.1f", "", 1.0)

#line 4
      self.wtemp    = widget.LabeledValue((130,35), self.disp, "%3.1f", " C", 25.0)
#line 5
      self.wdop     = widget.LabeledValue((130,45), self.disp, "%3.1f", " dop", 1.0)
#line 6
      self.wsats    = widget.LabeledValue((130,55), self.disp, "%02d/%02d", " SVs", (10,10))
#compass
      self.wcompass = widget.Compass((208, 32), self.disp, 31, [(15,28)], "%03d", 0)

   def GettingFocus(self):
      pass

   def InitDraw(self):
      screen.Screen.InitDraw(self, "GPS Nav")
      if self.apmenabled: self.wapm.InitDraw()
      self.wspeed.InitDraw()
      self.walt.InitDraw()
      self.wvspeed.InitDraw()
      self.wlat.InitDraw()
      self.wlon.InitDraw()
      self.wclock.InitDraw()

      self.wcourse.InitDraw()
      self.wcourse2.InitDraw()
      self.wtemp.InitDraw()
      self.wdop.InitDraw()
      self.wsats.InitDraw()
      self.wcompass.InitDraw()

   def Draw(self):
      v   = self.db.Get("gps/vector")
      vv  = self.db.Get("gps/vvector")
      h   = self.db.Get("gps/pos/here")

      if self.apmenabled:
         self.power.update()
         pstate = self.power.charging_state()
         if pstate == 0:
            pch = "-"
         elif pstate > 0 or pstate < 3:
            pch = "+"
         else:
            pch = "?"
         ppercent = self.power.percent()
         ptime = self.power.time()
         phour = int(ptime / 60)
         pmin = int(ptime - (phour * 60))
         self.wapm.Update((ppercent,pch,phour,pmin))
         self.wapm.Draw()

#line1
      self.wspeed.Update(v.speed_mph)
      self.wspeed.Draw()
#line2
      self.walt.Update(int(h.alt_f))
      self.walt.Draw()
      self.wvspeed.Update(vv.fpm)
      self.wvspeed.Draw()
#line3
      self.wlat.Update(h.GetLat())
      self.wlat.Draw()
#line4
      self.wlon.Update(h.GetLon())
      self.wlon.Draw()
#line5
      self.wclock.Draw()


#line1
      self.wcourse.Update(units.CompassOrd3(v.course))
      self.wcourse.Draw()
#line2
      self.wcourse2.Update(v.course)
      self.wcourse2.Draw()
#line4
      self.wtemp.Update(self.db.Get("gps/temp"))
      self.wtemp.Draw()
#line5
      self.wdop.Update(self.db.Get("gps/dop"))
      self.wdop.Draw()
#line6
      self.wsats.Update((self.db.Get("gps/sat/tracking"), self.db.Get("gps/sat/visible")))
      self.wsats.Draw()

#compass
      self.wcompass.Update(int(v.course))
      self.wcompass.Draw()

   def HandleCommand(self):
      screen.Screen.HandleCommand(self)
