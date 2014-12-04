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

import time, screen, waypoint, vector, widget, units, aprs, copy

class APRSScreen(screen.Screen):
   def __init__(self, db):
      screen.Screen.__init__(self, db)
      self.id = id
      self.page = 0
      self.mininav = widget.MiniNav((126,0), self.disp, self.db)
      self.wlines = [widget.APRSLine((0,10), self.disp, self.db),
                     widget.APRSLine((0,18), self.disp, self.db),
                     widget.APRSLine((0,26), self.disp, self.db),
                     widget.APRSLine((0,34), self.disp, self.db),
                     widget.APRSLine((0,42), self.disp, self.db),
                     widget.APRSLine((0,50), self.disp, self.db)]
      self.numlines = len(self.wlines)

      self.wscounter = widget.LabeledValue((0,  58),self.disp, "%3d-%3d OF %3d", "", (0,6,43), 4)
      self.wssort    = widget.LabeledValue((66, 58),self.disp, "SORT: %s", "", "DISTANCE", 4)
      self.wsfilter  = widget.LabeledValue((132,58),self.disp, "FILTER: %s", "", "NONE", 4)

      try:
         import apm
         self.apmenabled = 1
         self.wapm = widget.LabeledValue((83,0), self.disp, "%c%2d:%02d", "", (' ',0,0))
         self.power = apm.Apm()
      except ImportError:
         self.apmenabled = 0

   def InitDraw(self):
      screen.Screen.InitDraw(self, "APRS Stations")
      if self.apmenabled: self.wapm.InitDraw()
      self.mininav.InitDraw()
      self.disp.Line((120,8),(239,8))
      for w in self.wlines:
         w.InitDraw()

      self.disp.SetFont(5)
      self.wscounter.InitDraw()
      self.wssort.InitDraw()
      self.wsfilter.InitDraw()
      self.disp.SetFont(1)

   def Draw(self):
      if self.apmenabled:
         self.power.update()
         pstate = self.power.charging_state()
         if pstate == 0:
            pch = "-"
         elif pstate > 0 or pstate < 3:
            pch = "+"
         else:
            pch = "?"
         ptime = self.power.time()
         phour = int(ptime / 60)
         pmin = int(ptime - (phour * 60))
         self.wapm.Update((pch,phour,pmin))
         self.wapm.Draw()

      self.mininav.Draw()
      calls = self.db.Get("aprs/byconfig")

      sorttype = self.db.Get("config/aprs/sort")
      filtertype = self.db.Get("config/aprs/filter")
      filterdist = self.db.Get("config/aprs/maxdist")

      i = self.page * self.numlines
      for w in self.wlines:
         if i < len(calls):
            w.SetStation(calls[i])
         else:
            w.SetStation("")
         i += 1

      for w in self.wlines:
         w.Draw()

      lastnumonpage = self.page * self.numlines + self.numlines
      if lastnumonpage > len(calls): lastnumonpage = len(calls)
      self.wscounter.Update((self.page*self.numlines + 1, 
                             lastnumonpage,
                             len(calls)))
      self.disp.SetFont(5)
      self.wscounter.Draw()
      self.wssort.Update(sorttype.upper())
      self.wssort.Draw()

      filterdesc = "%s" % filtertype.upper()
      if filterdist:
         filterdesc += " <%dMI" % filterdist
      self.wsfilter.Update(filterdesc)
      self.wsfilter.Draw()
      self.disp.SetFont(1)

   def HandleCommand(self):
      command = self.commandq.get(1)
      if command == "esc":
         self.db.Get("global/router").Relinquish()
      elif command == "left":
         for w in self.wlines:
            w.PrevCol()
      elif command == "right":
         for w in self.wlines:
            w.NextCol()
      elif command == "up":
         self.page = max(self.page - 1, 0)
      elif command == "down":
         self.page += 1


class APRSDetailScreen(screen.Screen):
   def __init__(self, db):
      screen.Screen.__init__(self, db)
      self.id = id
      self.stationidx = 0
      self.call = ""
      self.col = 0
      self.statuscycle = 0.0

      self.mininav = widget.MiniNav((126,0), self.disp, self.db)
      self.num =     widget.LabeledValue((72, 0), self.disp, "%3d/%-3d", "", (123,456))

      self.InitX = [self.Init0, self.Init1]
      self.InitDrawX = [self.InitDraw0, self.InitDraw1]
      self.DrawX = [self.Draw0, self.Draw1]
      self.numcol = len(self.InitX)

   def Init(self):
      self.InitX[self.col]()
  
   def Init0(self):
      self.wcall   = widget.LabeledValue((0, 10),  self.disp, "%-9s", "", "KF6UZI-11")
      self.wsym    = widget.LabeledValue((60,10),  self.disp, "%-10s", " ", "0123456789")
      self.wtime   = widget.LabeledValue((126,10), self.disp, "%06s", "", "12:14s")

      #station compass
      self.wstcomp = widget.Compass((180, 28), self.disp, 18, [(0,16)], "%03d", 1)
      #me compass
      self.wmecomp = widget.Compass((220, 28), self.disp, 18, [(0,16), (0,9)], "", 0)

      self.wdist   = widget.LabeledValue((0, 19), self.disp, "%7s", " ", "123.4mi")
      self.wcrs    = widget.LabeledValue((48,19), self.disp, "%3s", " ", "SSW")
      self.wsrc    = widget.LabeledValue((72, 19), self.disp, "%15s", "", "GLL RMC")

      self.wmovorphg  = widget.LabeledValue((0,29), self.disp, "%-14s", " ", "012345678901234")

      self.wlat    = widget.LabeledValue((0, 39), self.disp, "%s", "", "")
      self.wlon    = widget.LabeledValue((0, 48), self.disp, "%s", "", "")
      self.walt    = widget.LabeledValue((72,48), self.disp, "%5d", "ft", 10123)

      self.wstatus = widget.LabeledValue((0, 57), self.disp, "%s", "", "")

   def Init1(self):
      self.wcall   = widget.LabeledValue((0, 10),  self.disp, "%-9s", "", "KF6UZI-11")
      self.wsym    = widget.LabeledValue((60,10),  self.disp, "%-10s", " ", "0123456789")
      self.wtime   = widget.LabeledValue((126,10), self.disp, "%06s", "", "12:14s")

      #wind compass
      self.wstcomp = widget.Compass((180, 28), self.disp, 18, [(0,16)], "%03d", 1)
      #me compass
      self.wmecomp = widget.Compass((220, 28), self.disp, 18, [(0,16), (0,9)], "", 0)

      self.wdist   = widget.LabeledValue((0, 19), self.disp, "%7s", " ", "123.4mi")
      self.wcrs    = widget.LabeledValue((48,19), self.disp, "%3s", " ", "SSW")
      self.wsrc    = widget.LabeledValue((72, 19), self.disp, "%15s", "", "GLL RMC")

      self.wwind   = widget.LabeledValue((0,29), self.disp, "%23s", "", "Wind NW @ 10 gust 50mph")

      #temperature, humidity, barometer
      self.wtemp   = widget.LabeledValue((0, 39), self.disp, "%5.1f", "F", 100.0)
      self.whumid  = widget.LabeledValue((42, 39), self.disp, "%3d", "%", 100)
      self.wbaro   = widget.LabeledValue((72, 39), self.disp, "%6.1f", "mbar", 1004.2)
      #rain1 rain2 rain3
      self.wrain   = widget.LabeledValue((0, 48), self.disp, "%5.2f\" %5.2f\" %5.2f\"", "", (13.0,13.0,13.0))

      self.wstatus = widget.LabeledValue((0, 57), self.disp, "%s", "", "")

   def InitDraw(self):
      screen.Screen.InitDraw(self, "APRS Detail")
      self.mininav.InitDraw()
      self.num.InitDraw()
      self.disp.Line((120,8),(239,8))
      self.call = ""
      self.NewIdx()

   def InitDraw0(self):
      self.wcall.InitDraw()
      self.wsym.InitDraw()
      self.wtime.InitDraw()

      self.wstcomp.InitDraw()
      self.wmecomp.InitDraw()

      self.wdist.InitDraw()
      self.wcrs.InitDraw()
      self.wsrc.InitDraw()

      self.wmovorphg.InitDraw()

      self.wlat.InitDraw()
      self.wlon.InitDraw()
      self.walt.InitDraw()

      self.wstatus.InitDraw()

   def InitDraw1(self):
      self.wcall.InitDraw()
      self.wsym.InitDraw()
      self.wtime.InitDraw()

      self.wstcomp.InitDraw()
      self.wmecomp.InitDraw()

      self.wdist.InitDraw()
      self.wcrs.InitDraw()
      self.wsrc.InitDraw()

      self.wwind.InitDraw()
      self.wtemp.InitDraw()
      self.whumid.InitDraw()
      self.wbaro.InitDraw()
      self.wrain.InitDraw()

      self.wstatus.InitDraw()

   def Draw(self):
      self.calls = self.db.Get("aprs/byconfig")
      if self.call:
         if self.call in self.calls:
            self.stationidx = self.calls.index(self.call)
            self.num.Update((self.stationidx+1, len(self.calls)))
         else: # station went away!
            self.stationidx = 0
            self.NewIdx()
            return

      self.mininav.Draw()
      self.num.Draw()
      if not self.call:
         self.NewIdx()
         return

      self.here = self.db.Get("gps/pos/here")
      self.v    = self.db.Get("gps/vector")

      try :
         self.station = self.db.Get("aprs/stations")[self.call]
      except KeyError:
         return
      self.DrawX[self.col]()

   def Draw0(self):
      self.wcall.Update(self.call)
      self.wcall.Draw()

      self.wsym.Update(self.station.GetSym())
      self.wsym.Draw()

      self.wtime.Update(self.station.GetAgeStrLong())
      self.wtime.Draw()

      if self.station.where.Valid():
         self.wstcomp.Update(self.station.v.course)
         self.wstcomp.Draw()

      if self.here.Valid():
         self.wmecomp.Update(self.here.BearingTo(self.station.where), 0)
         self.wmecomp.Update(self.v.course, 1)
         self.wmecomp.Draw()

      self.wdist.Update(self.MakeDistStr())
      self.wdist.Draw()

      if self.station.where.Valid():
         self.wcrs.Update(units.CompassOrd3(self.here.BearingTo(self.station.where)))
      else:
         self.wcrs.Update(0)
      self.wcrs.Draw()

      self.wsrc.Update(" ".join(self.station.source))
      self.wsrc.Draw()

      if self.station.HavePHG():
         self.wmovorphg.Update(self.station.GetPHGStr())
      else:
         self.wmovorphg.Update(self.MakeMovingStr())
      self.wmovorphg.Draw()

      if self.station.where.Valid():
         self.wlat.Update(self.station.where.GetLat())
         self.wlon.Update(self.station.where.GetLon())
         self.walt.Update(self.station.where.alt_f)
      else:
         self.wlat.Update(" " * 11)
         self.wlon.Update(" " * 11)
         self.walt.Update(0)

      self.wlat.Draw()
      self.wlon.Draw()
      self.walt.Draw()


      #status line
      numstatuses = len(self.station.status)
      if numstatuses:
         statstr = self.station.status[int(self.statuscycle) % numstatuses]
         if len(statstr) > 40:
            statstr = statstr[0:40]
         statstr = statstr + (" " * (40 - len(statstr)))

      else:
         statstr = " " * 40

      self.wstatus.Update(statstr)
      self.wstatus.Draw()
      self.statuscycle += .03

   def Draw1(self):
      self.wcall.Update(self.call)
      self.wcall.Draw()

      self.wsym.Update(self.station.GetSym())
      self.wsym.Draw()

      self.wtime.Update(self.station.GetAgeStrLong())
      self.wtime.Draw()

      if self.station.where.Valid():
         self.wstcomp.Update(self.station.v.course)
         self.wstcomp.Draw()

      if self.here.Valid():
         self.wmecomp.Update(self.here.BearingTo(self.station.where), 0)
         self.wmecomp.Update(self.v.course, 1)
         self.wmecomp.Draw()

      self.wdist.Update(self.MakeDistStr())
      self.wdist.Draw()

      if self.station.where.Valid():
         self.wcrs.Update(units.CompassOrd3(self.here.BearingTo(self.station.where)))
      else:
         self.wcrs.Update(0)
      self.wcrs.Draw()

      self.wsrc.Update(" ".join(self.station.source))
      self.wsrc.Draw()

      if self.station.wxvalid:
         self.wwind.Update("Wind %2s @%3.0f gust%3dmph" % (units.CompassOrd2(self.station.v.course), self.station.v.speed_mph, self.station.gust))
         self.wtemp.Update(self.station.temperature)
         self.whumid.Update(self.station.humidity)
         self.wbaro.Update(self.station.barometer)
         self.wrain.Update((self.station.rain[0], self.station.rain[1], self.station.rain[2]))
      else:
         self.wwind.Update("     No WX data     ")
         self.wtemp.Update(0)
         self.whumid.Update(0)
         self.wbaro.Update(0.0)
         self.wrain.Update((0.0, 0.0, 0.0))

      self.wwind.Draw()
      self.wtemp.Draw()
      self.whumid.Draw()
      self.wbaro.Draw()
      self.wrain.Draw()

      #status line
      numstatuses = len(self.station.status)
      if numstatuses:
         statstr = self.station.status[int(self.statuscycle) % numstatuses]
         if len(statstr) > 40:
            statstr = statstr[0:40]
         statstr = statstr + (" " * (40 - len(statstr)))

      else:
         statstr = " " * 40

      self.wstatus.Update(statstr)
      self.wstatus.Draw()
      self.statuscycle += .03

   def MakeDistStr(self):
      if not self.station.where.Valid():
         dstr = "NoPos"
      else:
         dist = self.here.DistanceTo(self.station.where)
         if dist >= 0.5:
            dstr = "%5.1fmi" % dist
         else:
            dstr = "%4.0fft" % units.m2f(units.mi2km(dist) * 1000)
      return dstr

   def MakeMovingStr(self):
      if self.station.v.IsMoving():
         return "%3.0fmph %2s" % (self.station.v.speed_mph, units.CompassOrd2(self.station.v.course))
      else:
         return "          "

   def EraseCols(self):
      self.disp.Rect((0, 27),(160, 56), 0, 1)

   def NewIdx(self):
      self.calls = self.db.Get("aprs/byconfig")
      if len(self.calls) == 0:
         return

      if self.stationidx < 0:
         self.stationidx = 0
      elif self.stationidx >= len(self.calls):
         self.stationidx = len(self.calls) - 1

      newcall = self.calls[self.stationidx]
      if self.call != newcall:
         self.call = newcall
         self.ReInit()

   def ReInit(self):
      self.Init()
      self.EraseCols()
      self.InitDrawX[self.col]()

   def PrevCol(self):
      if self.col > 0:
         self.col -= 1
         self.ReInit()

   def NextCol(self):
      if self.col < self.numcol - 1:
         self.col += 1
         self.ReInit()

   def HandleCommand(self):
      command = self.commandq.get(1)
      if command == "esc":
         self.db.Get("global/router").Relinquish()
      elif command == "left":
         self.PrevCol()
      elif command == "right":
         self.NextCol()
      elif command == "up":
         self.stationidx -= 1
         self.NewIdx()
      elif command == "down":
         self.stationidx += 1
         self.NewIdx()

