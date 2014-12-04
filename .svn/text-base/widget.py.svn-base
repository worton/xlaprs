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

import time, db, math, copy, waypoint, units, types, vector


def deg2rad(deg): return (deg - 90.0) * math.pi / 180.0

class Compass(object):
   def __init__(self, center, display, radius, lengths, textfmt="", movetext=0):
      self.center = center
      self.radius = radius
      self.display = display
      self.lengths = lengths
      self.textfmt = textfmt
      self.movetext = movetext

   def InitDraw(self):
      self.val = [0] * len(self.lengths)
      self.newval = [0] * len(self.lengths)

      self.display.Rect((self.center[0]-self.radius,self.center[1]-self.radius),
                        (self.center[0]+self.radius,self.center[1]+self.radius),
                        0, 1)
      self.display.Circle(self.center, self.radius)
      if self.textfmt: self.CalcTextExtents()

   def CalcTextExtents(self):
      s = self.textfmt % 200
      self.upper = (self.center[0]-(len(s)*3), self.center[1]-9,  #topleft
                    self.center[0]+(len(s)*3), self.center[1]-1)  #bottomright
      self.lower = (self.center[0]-(len(s)*3), self.center[1]+3,
                    self.center[0]+(len(s)*3), self.center[1]+11)
      

   def Update(self, newval, which=0):
      self.newval[which] = newval

   def Draw(self):
      if self.newval != self.val:
         self.display.SetColor(0)
         first = 1
         for (new, old, len) in map(None, self.newval, self.val, self.lengths):
            if self.textfmt and first and self.movetext: self.DoText(old, 1); first = 0
            self.DoLine(old, len)
            
         self.display.Rect((self.center[0]-1, self.center[1]-1),
                           (self.center[0]+1, self.center[1]+1), 1, 1)
         self.display.SetColor(1)

         first = 1
         for (new, old, len) in map(None, self.newval, self.val, self.lengths):
            if self.textfmt and first: self.DoText(new, 0); first = 0
            self.DoLine(new, len)

         self.val = copy.copy(self.newval)

   def DoText(self, heading, erase):
      s = self.textfmt % heading
      if erase:
         if (heading < 270 and heading > 90) or not self.movetext:
            self.display.Rect((self.upper[0], self.upper[1]),
                              (self.upper[2], self.upper[3]), 0, 1)
         else:
            self.display.Rect((self.lower[0], self.lower[1]),
                              (self.lower[2], self.lower[3]), 0, 1)

      else:
         if (heading < 270 and heading > 90) or not self.movetext:
            self.display.SetPos((self.upper[0], self.upper[1]))
         else:
            self.display.SetPos((self.lower[0], self.lower[1]))
         self.display.Write(s)

   def DoLine(self, heading, len):
      frm = (self.center[0] + (len[0] * math.cos(deg2rad(heading))), 
             self.center[1] + (len[0] * math.sin(deg2rad(heading))))
      to = (self.center[0] + (len[1] * math.cos(deg2rad(heading))), 
            self.center[1] + (len[1] * math.sin(deg2rad(heading))))
#      self.display.Line(self.center, to)
      self.display.Line(frm, to)

   
class LabeledValue(object):
   def __init__(self, where, display, format, label, sampleval, charwidth=6):
      self.where = where
      self.display = display
      self.format = format
      self.label = label
      self.sampleval = sampleval
      self.charwidth = charwidth

      self.val = None
      self.newval = None

   def Update(self, newval):
      self.newval = newval

   def InitDraw(self):
      self.val = None
      self.newval = None
      if len(self.label):
         #matrix orbital set position command apparent puts char in exact position you tell it to disregarding 
         #the font spacing setting (as they document), UNLESS the fist character you're putting is ' '  WTF?
         if self.label[0] == ' ':
            labelpos = (self.where[0] + (len(self.format % self.sampleval) * self.charwidth), self.where[1])
         else:
            labelpos = (1 + self.where[0] + (len(self.format % self.sampleval) * self.charwidth), self.where[1])
         self.display.SetPos(labelpos)
         self.display.Write(self.label)

   def Draw(self):
      if self.val != self.newval:
         self.val = self.newval
         self.display.SetPos(self.where)
         self.display.Write(self.format % self.val)


class GPSClock(object):
   def __init__(self, where, display, db, charwidth=6):
      self.where = where
      self.display = display
      self.db = db
      self.charwidth = charwidth


   def InitDraw(self):
      self.lasttimestr = "00:00:00"
      self.lastdatestr = "00/00/00"

   def Draw(self):
#      now = time.localtime()
      now = [0,0,0,0,0,0,0,0,0]
      now[0]  = self.db.Get("gps/time/year")
      now[1]  = self.db.Get("gps/time/month")
      now[2]  = self.db.Get("gps/time/day")

      now[3]  = self.db.Get("gps/time/hour")
      now[4]  = self.db.Get("gps/time/minute")
      now[5]  = self.db.Get("gps/time/second")

      now = time.mktime(now)
      now += self.db.Get("config/misc/tz") * 3600
      now = time.localtime(now)

      timestr = time.strftime("%02H:%02M:%02S", now)
      datestr = time.strftime("%02m/%02d/%Y", now)

      if timestr != self.lasttimestr:
         self.display.SetPos(self.where)
         self.display.Write(timestr)
         self.lasttimestr = timestr

      if datestr != self.lastdatestr:
         self.display.SetPos((self.where[0] + ((len(timestr)+1) * self.charwidth), self.where[1]))
         self.display.Write(datestr)
         self.lastdatestr = datestr

class MiniNav(object):
   def __init__(self, where, display, db):
      self.where = where
      self.disp = display
      self.db = db
#"01234567890123456789"
#"178.1mph NNW 11293' "
      self.w = LabeledValue(self.where, self.disp, "%5.1fmph %3s %5d'", "", (123.1, "NNW", 11211))

   def InitDraw(self):
      self.w.InitDraw()

   def Draw(self):
      v = self.db.Get("gps/vector")
      h = self.db.Get("gps/pos/here")
      self.w.Update((v.speed_mph, units.CompassOrd3(v.course), int(h.alt_f)))
      self.w.Draw()


class APRSLine(object):
   def __init__(self, where, display, db):
      self.where = where
      self.disp = display
      self.db = db
      self.col = 0

      self.call = ""
      self.statuscycle = 0.0

      self.InitX = [self.Init0, self.Init1, self.Init2, self.Init3]
      self.InitDrawX = [self.InitDraw0, self.InitDraw1, self.InitDraw2, self.InitDraw3]
      self.DrawX = [self.Draw0, self.Draw1, self.Draw2, self.Draw3]

      self.wcall = LabeledValue(self.where, self.disp, "%-9s", "", "KF6UZI-11")
      self.Init()

   def InitDraw(self):
      if not self.call: #just erase and be content being a blank line
         self.disp.SetPos(self.where)
         self.disp.Write(" " * 40)
      else:
         self.wcall.InitDraw()
         self.InitDrawX[self.col]()

   def Draw(self):
      if not self.call:
         return

      self.here = self.db.Get("gps/pos/here")
      try :
         self.station = self.db.Get("aprs/stations")[self.call]
      except KeyError:
         return

      self.wcall.Update(self.station.call)
      self.wcall.Draw()
      self.DrawX[self.col]()

   def SetStation(self, call):
      if self.call != call:   #we got switched!
         self.call = call
         self.NewCol()
   def NextCol(self):
      self.col = min(self.col + 1, len(self.InitX) - 1)
      self.NewCol()
   def PrevCol(self):
      self.col = max(self.col - 1, 0)
      self.NewCol()
   def NewCol(self):
      self.Init()
      self.InitDraw()

   def Init(self):
      self.InitX[self.col]()
   def Init0(self):
      self.wsym  = LabeledValue((self.where[0]+60,self.where[1]), self.disp, "%-10s", " ", "0123456789")
      self.wdist = LabeledValue((self.where[0]+126,self.where[1]), self.disp, "%7s", " @", "123.4mi")
      self.wcrs  = LabeledValue((self.where[0]+180,self.where[1]), self.disp, "%3d", " ", 270)
      self.walt  = LabeledValue((self.where[0]+204,self.where[1]), self.disp, "%5d", "'", 12345)
   def Init1(self):
      self.wmov  = LabeledValue((self.where[0]+60,self.where[1]), self.disp, "%-10s", " ", "0123456789")
      self.wdist = LabeledValue((self.where[0]+126,self.where[1]), self.disp, "%7s", " @", "123.4mi")
      self.wcrs  = LabeledValue((self.where[0]+180,self.where[1]), self.disp, "%3d", " ", 270)
      self.wtime = LabeledValue((self.where[0]+204,self.where[1]), self.disp, "   %03s", "", "45s")
   def Init2(self):
      self.wstat  = LabeledValue((self.where[0]+60,self.where[1]), self.disp, "%-30s", "", "Status blah blah")
   def Init3(self):
      self.wmice  = LabeledValue((self.where[0]+60,self.where[1]), self.disp, "%-14s", " ", "01234567890123")
      self.wsrc   = LabeledValue((self.where[0]+150,self.where[1]), self.disp, "%-15s", "", "012345678901234")
   

   def InitDraw0(self):
      self.wsym.InitDraw()
      self.wdist.InitDraw()
      self.wcrs.InitDraw()
      self.walt.InitDraw()
   def InitDraw1(self):
      self.wmov.InitDraw()
      self.wdist.InitDraw()
      self.wcrs.InitDraw()
      self.wtime.InitDraw()
   def InitDraw2(self):
      self.wstat.InitDraw()
   def InitDraw3(self):
      self.wmice.InitDraw()
      self.wsrc.InitDraw()



   def Draw0(self):
      self.wsym.Update(self.station.GetSym())
      self.wsym.Draw()
      
      self.wdist.Update(self.MakeDistStr())
      self.wdist.Draw()

      if self.station.where.Valid():
         self.wcrs.Update(int(self.here.BearingTo(self.station.where)))
      else:
         self.wcrs.Update(0)
      self.wcrs.Draw()

      self.walt.Update(int(self.station.where.alt_f))
      self.walt.Draw()

   def Draw1(self):
      self.wmov.Update(self.MakeMovingStr())
      self.wmov.Draw()
      
      self.wdist.Update(self.MakeDistStr())
      self.wdist.Draw()

      if self.station.where.Valid():
         self.wcrs.Update(int(self.here.BearingTo(self.station.where)))
      else:
         self.wcrs.Update(0)
      self.wcrs.Draw()

      self.wtime.Update(self.station.GetAgeStr())
      self.wtime.Draw()

   def Draw2(self):
      numstatuses = len(self.station.status)
      if numstatuses:
         statstr = self.station.status[int(self.statuscycle) % numstatuses]
         if len(statstr) > 30:
            statstr = statstr[0:30]
      else:
         statstr = " " * 30
      self.wstat.Update(statstr)
      self.wstat.Draw()
      self.statuscycle += .03

   def Draw3(self):
      if self.station.micemsg:
         self.wmice.Update(self.station.micemsg)
      elif self.station.p or self.station.g:
         self.wmice.Update(self.station.GetPHGStr())
      else:
         self.wmice.Update("")

      self.wmice.Draw()

      self.wsrc.Update(" ".join(self.station.source))
      self.wsrc.Draw()

   def MakeMovingStr(self):
      if self.station.v.IsMoving():
         return "%3.0fmph %2s" % (self.station.v.speed_mph, units.CompassOrd2(self.station.v.course))
      else:
         return self.station.GetSym()

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


class MesgLine(object):
   def __init__(self, where, display, db):
      self.where = where
      self.disp = display
      self.db = db
      self.col = 0
      self.mhash = ""

      self.mnum = 0
      self.messagecycle = 0.0

      self.InitX = [self.Init0]
      self.InitDrawX = [self.InitDraw0]
      self.DrawX = [self.Draw0]

      self.wmnum = LabeledValue(self.where, self.disp, "%2d", "", 1)
      self.wtype = LabeledValue((self.where[0]+12,self.where[1]), self.disp, "%c", "", 'b')
      self.wcall = LabeledValue((self.where[0]+18,self.where[1]), self.disp, "%-9s", "", "KF6UZI-11")
      self.wpointer = LabeledValue((self.where[0]+72,self.where[1]), self.disp, "%c","", '>')
      self.wstatus = LabeledValue((self.where[0]+222,self.where[1]), self.disp, "%3s", "", "[*]")
      self.Init()

   def InitDraw(self):
      if not self.mhash: #just erase and be content being a blank line
         self.disp.SetPos(self.where)
         self.disp.Write(" " * 40)
      else:
         self.wmnum.InitDraw()
         self.wpointer.InitDraw()
         self.wcall.InitDraw()
         self.wstatus.InitDraw()
         self.wtype.InitDraw()
         self.InitDrawX[self.col]()

   def Draw(self):
      if not self.mhash:
         return
      try :
         self.message = self.db.Get("aprs/messages")[self.mhash]
      except KeyError:
         return
      try :
         self.mnum = self.db.Get("aprs/messagelist").index(self.mhash) + 1
      except ValueError:
         return
      self.wmnum.Update(self.mnum)
      self.wmnum.Draw()
      self.wtype.Update(self.message.type)
      self.wtype.Draw()
      if self.message.mesgfrom == self.db.Get("config/tnc/mycall"):
         self.wcall.Update(self.message.mesgto)
      else:
         self.wcall.Update(self.message.mesgfrom)
      self.wcall.Draw()
      self.wpointer.Update(' ')
      self.wpointer.Draw()
      if self.message.acked:
         self.wstatus.Update("[%d]" % self.message.txtimes)
      else:
         self.wstatus.Update("{%d}" % self.message.txtimes)
      self.wstatus.Draw()
      self.DrawX[self.col]()

   def SetMessageHash(self, mhash):
      if self.mhash != mhash:   #we got switched!
         self.mhash = mhash
         self.NewCol()

   def NextCol(self):
      self.col = min(self.col + 1, len(self.InitX) - 1)
      self.NewCol()

   def PrevCol(self):
      self.col = max(self.col - 1, 0)
      self.NewCol()

   def NewCol(self):
      self.Init()
      self.InitDraw()

   def Init(self):
      self.InitX[self.col]()

   def Init0(self):
      self.wmessage  = LabeledValue((self.where[0]+78,self.where[1]), self.disp, "%-24s", "", "Status blah blah")

   def Init1(self):
      return

   def InitDraw0(self):
      self.wmessage.InitDraw()

   def InitDraw1(self):
      self.disp.SetPos((self.where[0]+102,self.where[1]))
      self.disp.Write(" " * 23)

   def Draw0(self):
      if len(self.message.message):
         start = int(self.messagecycle) * 23
         if start > len(self.message.message):
            self.messagecycle = 0.0
            start = 0
         mesgstr = self.message.message[start:]
         if len(mesgstr) > 23:
            mesgstr = mesgstr[0:23]
      else:
         mesgstr = " " * 23
      self.wmessage.Update(mesgstr)
      self.wmessage.Draw()
      self.messagecycle += .03

   def Draw1(self):
      return


class ConfigLine(object):
   def __init__(self, where, display, db):
      self.where = where
      self.disp = display
      self.key = ""
      self.db = db
      self.editing = 0

#screen calls me on these
   def SetKey(self, key):
      if self.key != key:  #load up the new guy
         self.key = key
         self.valueat = (self.where[0] + (6 * (len(self.key) + 1 - 7)), self.where[1])
         self.m = {}
         self.InitDraw()

   def Left(self):
      if self.type == "int":
         self.inc = min(self.inc*10, 1000)
      elif self.type == "str":
         if not self.m.has_key("choices"):
            self.cur = max(self.cur-1, 0)

   def Right(self):
      if self.type == "int":
         self.inc = max(self.inc/10, 1)
      elif self.type == "str":
         if not self.m.has_key("choices"):
            self.cur = min(self.cur+1, self.m["max"] - 1)

   def Up(self):
      if self.type == "int":
         self.val += self.inc
      elif self.type == "str":
         if self.m.has_key("choices"):
            self.cur = min(self.cur+1, len(self.m["choices"])-1)
            self.val = self.m["choices"][self.cur]
         else:
            s = list(self.val)
            c = ord(s[self.cur])
            s[self.cur] = chr(min(c + 1, ord('~')))
            self.val = "".join(s)
            
            

   def Down(self):
      if self.type == "int":
         self.val -= self.inc
      elif self.type == "str":
         if self.m.has_key("choices"):
            self.cur = max(self.cur-1, 0)
            self.val = self.m["choices"][self.cur]
         else:
            s = list(self.val)
            c = ord(s[self.cur])
            s[self.cur] = chr(max(c - 1, ord(' ')))
            self.val = "".join(s)

   def Edit(self):
      self.editing = 1
      if self.type == "int":
         self.inc = 1
      elif self.type == "str":
         if self.m.has_key("choices"):
            self.cur = self.m["choices"].index(self.val)
         else:  #just regular string edit
            self.cur = 0
         
   def Esc(self):
      self.editing = 0

   def Save(self):
      self.editing = 0
      self.db.Put(self.key, self.val)

   def FillVal(self, val):
      available = (240 - self.valueat[0]) / 6
      if len(val) > available:
         return val[0:available]
      else:
         return val + (" " * (available - len(val)))

   def InitDraw(self):
      self.disp.SetPos(self.where)
      if self.key:
         self.disp.Write(self.key[7:] + " ")

         self.val = self.db.Get(self.key)
         self.meta = self.db.Get("meta"+self.key)
         self.ParseMeta()

         self.disp.SetPos(self.valueat)
         vstr = ""
         if isinstance(self.val, types.IntType):
            self.type = "int"
            vstr = "%d" % self.val
         elif isinstance(self.val, types.StringType):
            self.type = "str"
            if "max" in self.m:
               self.val = self.val + (" " * (self.m["max"] - len(self.val)))
            vstr = "%s" % self.val
         self.disp.Write(self.FillVal(vstr))
      else:
         self.disp.Write(" " * 39)

   def Draw(self):
      if self.editing:
         self.disp.SetPos(self.valueat)
         if self.type == "int":
            self.disp.Write(self.FillVal("%d" % self.val))
         elif self.type == "str":
            if self.m.has_key("choices"):
               self.disp.Write(self.FillVal("%s" % self.val))
            else:
               editstr = "%s>%s" % (self.val[0:self.cur], self.val[self.cur:])
               self.disp.Write(self.FillVal(editstr))
      else:
         if self.type == "str" and not self.m.has_key("choices"):  
            #this is the only one we need to show when coming out of edit
            self.disp.SetPos(self.valueat)
            self.disp.Write(self.FillVal(self.val))

   def ParseMeta(self):
      for pair in self.meta.split():
         (var, val) = pair.split(":")
         if var == "choices":
            self.m[var] = val.split("/")
         elif var in ["max", "min", "isbool"]:
            self.m[var] = int(val)
         else:
            continue
#         print var, self.m[var]
