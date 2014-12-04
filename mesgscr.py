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

class MesgScreen(screen.Screen):
   def __init__(self, db):
      screen.Screen.__init__(self, db)
      self.id = id
      self.page = 0
      self.mininav = widget.MiniNav((126,0), self.disp, self.db)
      self.wlines = [widget.MesgLine((0,10), self.disp, self.db),
                     widget.MesgLine((0,18), self.disp, self.db),
                     widget.MesgLine((0,26), self.disp, self.db),
                     widget.MesgLine((0,34), self.disp, self.db),
                     widget.MesgLine((0,42), self.disp, self.db),
                     widget.MesgLine((0,50), self.disp, self.db)]
      self.numlines = len(self.wlines)

      self.wscounter = widget.LabeledValue((0,58),self.disp, "%3d-%3d OF %d", "", (0,6,43), 4)
      self.wssort    = widget.LabeledValue((66,58),self.disp, "SORT: %s", "", "TIME", 4)
      self.wsfilter  = widget.LabeledValue((132,58),self.disp, "FILTER: %s", "", "NONE", 4)

   def InitDraw(self):
      screen.Screen.InitDraw(self, "APRS Messages")
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
      self.mininav.Draw()
      messages = self.db.Get("aprs/messagelist")

      sorttype = "time"
      filtertype = "none"

      i = self.page * self.numlines
      for w in self.wlines:
         if i < len(messages):
            w.SetMessageHash(messages[i])
         else:
            w.SetMessageHash("")
         i += 1

      for w in self.wlines:
         w.Draw()

      lastnumonpage = self.page * self.numlines + self.numlines
      if lastnumonpage > len(messages): lastnumonpage = len(messages)
      self.wscounter.Update((self.page*self.numlines + 1, 
                             lastnumonpage,
                             len(messages)))
      self.disp.SetFont(5)
      self.wscounter.Draw()
      self.wssort.Update(sorttype.upper())
      self.wssort.Draw()

      filterdesc = "%s" % filtertype.upper()
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

