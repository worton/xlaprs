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

import threading, time, display

class Router(threading.Thread):
   def __init__(self, db):
      threading.Thread.__init__(self)
      self.running = 0
      self.db = db;

      self.focus = self
      self.esccount = 0
      self.curscr = None
      self.screenlist = self.db.Get("global/screenlist")

      for scr in self.screenlist:
         scr.Start()

      self.curscridx = 0
      self.maxscr = len(self.screenlist) - 1

      self.db.Put("global/router", self)
      self.status = "initted"

#valid commands
#"up", "down", "left", "right", "enter", "esc", "beacon", "usr1"
   def EnqueueCommand(self, command):
#      print "router> command %s" % command
      if command == "beacon":
         self.db.Put("aprs/beaconnow", 1)
      elif self.focus == self:
         if command == "up":
            self.curscridx = max(0, self.curscridx-1)
            self.SwitchTo(self.curscridx)
         elif command == "down": 
            self.curscridx = min(self.maxscr, self.curscridx+1)
            self.SwitchTo(self.curscridx)
         elif command == "enter":
            self.focus = self.curscr
         elif command == "esc":
            self.esccount += 1
            if self.esccount > 10:
               self.db.Get("global/display").Setup()
               self.esccount = 0

      else:
         self.curscr.EnqueueCommand(command)

   def SwitchTo(self, newscridx):
      if self.curscr:
         self.curscr.Hide()

      if newscridx == -1: return
     
      self.curscr = self.screenlist[newscridx]
      self.curscr.Show()

#Screens call this to give up focus
   def Relinquish(self):
      self.focus = self

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
      print "router> running"
      self.SwitchTo(0)
      while self.running:
         time.sleep(1)
      self.SwitchTo(-1)
      
      for scr in self.screenlist:
         scr.Stop()

      print "router> exiting"



