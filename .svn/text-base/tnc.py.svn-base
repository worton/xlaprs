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

import serial, threading, time, string

class AX25Packet:
   def __init__(self):
      self.frm = ""
      self.to = ""
      self.repeaters = []
      self.data = ""

   def __str__(self):
      return "%s > %s v %s : %s" % (self.frm, self.to, repr(self.repeaters), self.data)

   def AssembleCall(self, str, last):
#      print "kiss> assemble call %s" % str
      if "-" in str:
         (frm, ssid) = str.split("-")
         ssid = int(ssid)
      else:
         frm = str
         ssid = 0

      frm = "%-6s" % frm

      call = [chr(ord(char) << 1) for char in frm]
      ssidbyte = ssid << 1
      if last: ssidbyte |= 1
      call += chr(ssidbyte)
      return call

   def AssemblePacket(self):  #return string of bytes ready to tx
      tobytes = self.AssembleCall(self.to, 0)
      frmbytes = self.AssembleCall(self.frm, 0)
      reps = []
      i = 1
      for rep in self.repeaters:
         if len(self.repeaters) == i:
            reps.append(self.AssembleCall(rep, 1))
         else:
            reps.append(self.AssembleCall(rep, 0))
         i += 1

      control = chr(0x03)
      pid = chr(0xF0)
      data = self.data

      ax25bytes = tobytes
      ax25bytes += frmbytes
      for rep in reps:
         ax25bytes += rep
      ax25bytes += control
      ax25bytes += pid
      ax25bytes += self.data
      ax25bytes = "".join(ax25bytes)

      return ax25bytes

class Tnc(threading.Thread):
   rxq = []
   txq = []

   def HavePackets(self):   #ret bool
      if len(self.rxq) > 0 : return 1
      else: return 0

   def GetPacket(self):     #ret AX25Packet obj
      if self.HavePackets():
         return self.rxq.pop()
      else:
         return None

   def SendPacket(self, packet):
      self.txq.insert(0, packet)

class Kiss(Tnc):
   FEND = "\xC0"
   FESC = "\xDB"
   TFEND = "\xDC"
   TFESC = "\xDD"

   def __init__(self, port, db):
      threading.Thread.__init__(self)
      self.port = port
      self.db = db
      self.running = 0
      try:
         self.s = serial.Serial(port, 9600, rtscts=0, xonxoff=0, timeout=0.1)
      except:
         print "kiss> could not open serial port %d" % self.port

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
      print "kiss> running"
      data = ""
      self.s.flushInput()
      self.s.flushOutput()

      while self.running:
         if len(self.txq) > 0:
            self.DoTX()

         data = data + self.s.read(500)
         if string.find(data, self.FEND) >= 0:
            frames = data.split(self.FEND)
            if len(frames) > 0 and len(frames[-1]) > 0 and frames[-1][-1] != self.FEND:
               data = frames.pop()
            else:
               data = ""
            for frame in frames:
               if len(frame) > 0:
                  if ord(frame[0]) == 0:
                     #print "kiss> data frame: ", frame
                     frame = frame.replace(self.FESC + self.TFEND, self.FEND)
                     frame = frame.replace(self.FESC + self.TFESC, self.FESC)
                     if len(frame) > 14:
                        self.ParseAX25(frame[1:])
                  else:
                     print "kiss> rxed unknown KISS frame type"

         

         time.sleep(.1)
      print "kiss> exiting..."
      self.s.close()

   def InjectRX(self, packet):
      ax25bytes = packet.AssemblePacket()
      self.ParseAX25(ax25bytes)

   def DoTX(self):
      packet = self.txq.pop()
      ax25bytes = packet.AssemblePacket()
      ax25bytes = ax25bytes.replace(self.FESC, self.FESC + self.TFESC)
      ax25bytes = ax25bytes.replace(self.FEND, self.FESC + self.TFEND)
      kissframe = self.FEND + "\x00" + ax25bytes + self.FEND
      print repr(kissframe)
      self.s.write(kissframe)

   def ParseAX25(self, frame):
      #decode address field
      morecalls = 1
      i = 0
      calls = []

      try:
         while morecalls:
            call = string.join([chr(ord(byte) >> 1) for byte in frame[i:i+6]], "")
            call = string.strip(call)
        #next line barfs often
            ssid = (ord(frame[i+6]) >> 1) & 15
            if ssid > 0: call += "-%d" % ssid

            calls.append(call)
            morecalls = 1 - (ord(frame[i+6]) & 1)
            i += 7

   #WDOFIX check len here; big try block suffices for now :/
         control = ord(frame[i])
         i += 1
         pid = ord(frame[i])
         i += 1

         if control & 3:  #U frame
            if (control & 12) == 0 and (control & 224) == 0 and pid == 0xF0: # UI frame w/ no layer 3 protocol
               stripchars = ["\n", "\r"]
               data = frame[i:]
               while len(data) > 0 and data[-1] in stripchars:
                  data = data[:-1]
   #            print "kiss> %s: %s" % (repr(calls), data)
            else:
               print "kiss> U but non-I frame type"
               return
         else:
            print "kiss> Non-U frame type"
            return
      except:
         print "kiss> Error decoding frame; probably junk from TNC"
         return

      packet = AX25Packet()
      packet.to = calls[0]
      packet.frm = calls[1]
      if len(calls) > 2:
         packet.repeaters = calls[2:]
      packet.data = data
      self.rxq.insert(0, packet)
#      print packet






#KPC-3 stuff
#      while self.running:
#         data = data + self.s.read(500)
#         data = data.replace("\r", "")
#
#         if string.find(data, "\n") >= 0:
#            lines = [x for x in data.split("\n")]
#            if len(lines) > 0 and len(lines[-1]) > 0 and lines[-1][-1] != "\n":
#               data = lines.pop()
#            else:
#               data = ""
#            for line in lines:
#               if len(line) > 0:
#                  self.Parse(line)
#                
#         time.sleep(.2)
#
#
#
#      #hack off AX25 info
#      fromcall = line[0:line.find(">")]
#      tolist = string.split(line[line.find(">")+1 : line.find(":")], ",")
#      tocall = tolist[0]
#      if len(tolist) > 0: digis = tolist[1:]
#      data = line[line.find(">:") + 2:]
#
#      print "aprs> --- %s to %s via %s" % (fromcall, tocall, repr(digis))
#      print "aprs> data: %s" % data
#
#      type = data[0]
