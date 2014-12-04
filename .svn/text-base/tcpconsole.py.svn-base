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

from socket import *
import threading, time, select, router, string, types, re


class Tcpconsole(threading.Thread):
   def __init__(self, port, db):
      threading.Thread.__init__(self)
      self.port = port
      self.db = db
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

   def Handle(self, s):
      pass

   def run(self):
      print "tcpconsole> running"

      s = socket(AF_INET, SOCK_STREAM)
      s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
      s.bind(("", self.port))
      s.listen(3)
      
      clients = []

      while self.running:
         (i, o, e) = select.select(clients + [s], [], [], 1)

         if s in i:
            (client, addr) = s.accept()
            print "tcpconsole> accepted client from %s" % str(addr)
            clients.append(client)
            i.remove(s)

         for client in i:
            req = client.recv(100)
            req = req.replace("\n", "")
            req = req.replace("\r", "")
            if req[0:4] == "quit":
               clients.remove(client)
               client.close()

            elif req[0:6] == "getkey":
               client.send(str(self.db.Get(req[7:])) + "\n")

            elif req[0:6] == "getall":
               for (key, val) in self.db.GetAll():
                  client.send("%s: %s\n" % (key, str(val)))

            elif req[0:6] == "putkey":
               data = string.split(req," ",2)
               if len(data) > 2:
                  previous = self.db.Get(data[1])
                  if previous != None:
                     if isinstance(previous, types.IntType):
                        self.db.Put(data[1],int(data[2]));
                     elif isinstance(previous, types.StringType):
                        self.db.Put(data[1],str(data[2]));
                     client.send("%s\n" % (self.db.Get(data[1])))
                  else:
                     client.send("eh?  Unknown db key\n")
               else:
                  client.send("eh?\n")

# WARNING: this is just temporary and blindly does things and ignores
# all resemblences of locks or stuff...this is BAAAAD! -kglueck
            elif req[0:4] == "msg ":
               try:
                  msg = req[4:]
                  self.db.Put("aprs/msg", msg)
               except IndexError:
                  print "tcpconsole> bad message format"

            elif req[0:7] == "getmsg ":
               mid = req[7:]
               if re.match("^\d+$",mid):
                  #it's a message number, not a hash
                  mlist = self.db.Get("aprs/messagelist")
                  try:
                     mid = mlist[int(mid)]
                  except IndexError:
                     print "tcpconsole> bad message index"
               messages = self.db.Get("aprs/messages")
               if messages.has_key(mid):
                  client.send("%s\n" % messages[mid])
               else:
                  client.send("eh?  Unknown message id\n")

#controller commands
            elif len(req) and req[0] == "u":
               self.db.Get("global/router").EnqueueCommand("up")
            elif len(req) and req[0] == "d":
               self.db.Get("global/router").EnqueueCommand("down")
            elif len(req) and req[0] == "l":
               self.db.Get("global/router").EnqueueCommand("left")
            elif len(req) and req[0] == "r":
               self.db.Get("global/router").EnqueueCommand("right")
            elif len(req) and req[0] == "e":
               self.db.Get("global/router").EnqueueCommand("enter")
            elif len(req) and req[0] == "w":
               self.db.Get("global/router").EnqueueCommand("esc")
            elif req[0:6] == "beacon":
               self.db.Get("global/router").EnqueueCommand("beacon")
            else:
               client.send("eh?\n")

      s.close()
      print "tcpconsole> exiting..."

