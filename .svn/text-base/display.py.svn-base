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

import serial, threading, time, router


class Display(object):
   def __init__(self, db):
      self.db = db
      self.db.Put("global/display", self)

   def SetPos(self, point):
      pass
   def SetFont(self, fontnum):
      pass
   def SetColor(self, color):
      pass

   def Clear(self):
      pass
   def Pixel(self, point):
      pass
   def Line(self, frm, to):
      pass
   def Rect(self, topleft, bottomright, color, filled):
      pass
   def Circle(self, centerpoint, radius):
      x = 0
      y = radius
      d = 1 - radius
      self.DrawOctPix(centerpoint, (x, y))
      while y > x:
         if d < 0:
            d += x * 2 + 3  # Select E
            x += 1
         else:
            d += (x - y) * 2 + 5  # Select SE
            x += 1
            y -= 1
         self.DrawOctPix(centerpoint, (x, y))

   def Write(self, str):
      pass

   def InitStrip(self, num, topleft, bottomright):
      pass
   def ShiftStrip(self, num, right):
      pass
   def InitBar(self, num, type, topleft, bottomright):
      pass
   def SetBar(self, num, val):
      pass

#priv:

   def DrawOctPix(self, center, where):
      self.Pixel((center[0] + where[0], center[1] + where[1]))
      self.Pixel((center[0] + where[0], center[1] - where[1]))
      self.Pixel((center[0] - where[0], center[1] + where[1]))
      self.Pixel((center[0] - where[0], center[1] - where[1]))
      self.Pixel((center[0] + where[1], center[1] + where[0]))
      self.Pixel((center[0] + where[1], center[1] - where[0]))
      self.Pixel((center[0] - where[1], center[1] + where[0]))
      self.Pixel((center[0] - where[1], center[1] - where[0]))



class Glc(Display, threading.Thread):
   def __init__(self, port, db):
      threading.Thread.__init__(self)
      Display.__init__(self, db)
      self.port = port
      self.running = 0
      try:
         self.s = serial.Serial(port, 57600, rtscts=0, xon=1, timeout=1)
      except:
         print "glc> could not open serial port %d" % self.port

      #set xon to chars glc display wants to use
      self.s.setVSTART(255)
      self.s.setVSTOP(254)

      self.Setup()

      self.status = "initted"
      print "glc> initted"

   def Setup(self):
      self.SendCommand(58)
      self.s.write(chr(64)) #high level, 64 bytes
      self.s.write(chr(32))  #low level, 32 bytes

      self.SendCommand(82)  # set autoscroll off
      self.SendCommand(126) # set keypad auto-repeat on
      self.s.write(chr(0))

      self.SendCommand(49)  # switch to font 1
      self.s.write(chr(1))

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
      while self.running:
#         print "glc> tick"
         c = self.s.read(1)
         if len(c) == 1:
            if c == 'A':
               self.db.Get("global/router").EnqueueCommand("right")
            elif c == 'B':
               self.db.Get("global/router").EnqueueCommand("down")
            elif c == 'C':
               self.db.Get("global/router").EnqueueCommand("up")
            elif c == 'D':
               self.db.Get("global/router").EnqueueCommand("left")
            elif c == 'F':
               self.db.Get("global/router").EnqueueCommand("usr1")
            elif c == 'H':
               self.db.Get("global/router").EnqueueCommand("enter")
            elif c == 'G':
               self.db.Get("global/router").EnqueueCommand("esc")
            elif c == 'I':
               self.db.Get("global/router").EnqueueCommand("beacon")
#         time.sleep(1)

      print "glc> exiting..."
      self.s.close()

   def SetPos(self, point):
      self.SendCommand(121)
      self.s.write(chr(point[0]))
      self.s.write(chr(point[1]))

   def SetFont(self, fontnum):
      self.SendCommand(49)
      self.s.write(chr(fontnum))

   def SetColor(self, color):
      self.SendCommand(99)
      self.s.write(chr(color))

   def Clear(self):
      self.SendCommand(88)

   def SetBacklightOff(self):
      self.SendCommand(70)

   def SetBacklightOn(self):
      self.SendCommand(66)
      self.s.write(chr(0))

   def Pixel(self, point):
      self.SendCommand(112)
      self.s.write(chr(point[0]))
      self.s.write(chr(point[1]))
      
   def Line(self, frm, to):
      self.SendCommand(108)
      self.s.write(chr(frm[0]))
      self.s.write(chr(frm[1]))
      self.s.write(chr(to[0]))
      self.s.write(chr(to[1]))

   def Rect(self, topleft, bottomright, color, filled):
      if filled:
         self.SendCommand(120)
      else:
         self.SendCommand(114)
      self.s.write(chr(color))
      self.s.write(chr(topleft[0]))
      self.s.write(chr(topleft[1]))
      self.s.write(chr(bottomright[0]))
      self.s.write(chr(bottomright[1]))
      
   def Write(self, str):
      self.s.write(str)

   def InitStrip(self, num, topleft, bottomright):
      self.SendCommand(106)
      self.s.write(chr(num))
      self.s.write(chr(topleft[0]))
      self.s.write(chr(topleft[1]))
      self.s.write(chr(bottomright[0]))
      self.s.write(chr(bottomright[1]))

   def ShiftStrip(self, num, right):
      if right:
         num |= 128
      self.sendcommand(107)
      self.s.write(chr(num))

   def InitBar(self, num, type, topleft, bottomright):
      self.SendCommand(103)
      self.s.write(chr(num))
      self.s.write(chr(type))
      self.s.write(chr(topleft[0]))
      self.s.write(chr(topleft[1]))
      self.s.write(chr(bottomright[0]))
      self.s.write(chr(bottomright[1]))

   def SetBar(self, num, val):
      self.SendCommand(105)
      self.s.write(chr(num))
      self.s.write(chr(val))

#priv:

   def SendCommand(self, num):
      self.s.write(chr(254))
      self.s.write(chr(num))

