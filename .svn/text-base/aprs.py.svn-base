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

import threading, time, string, units, waypoint, tnc, copy, vector

class AprsMessage:
   def __init__(self):
      self.mesgfrom = ""       # callsign-SSID from
      self.mesgto = ""         # callsign-SSID who it was to
      self.type = ' '          # message type
      self.message = ""        # the payload...the message
      self.mesgid = ""         # message id if received/sent
      self.acked = 0           # have we received or sent an ack on this message?
      self.timestamp = 0       # when received
      self.txtimes = 0         # when we're the tx station, # times we've tx'd it
                               # when we're the rx station, # times we've rx'd it

   def Touch(self):
      self.timestamp = time.time()
      self.txtimes += 1

   def Hash(self): return hash("%s{%s" % (self.message,self.mesgid))

   def GetKey(self): return "%s/%s" % (self.mesgfrom,self.Hash())

   def Ack(self): self.acked += 1

   def GetAckStr(self): return ":%-9s:ack%s" % (self.mesgfrom,self.mesgid)

   def __str__(self):
      if len(self.mesgid):
         return "%s > %s : %s{%s" % (self.mesgfrom, self.mesgto, self.message, self.mesgid)
      else:
         return "%s > %s : %s" % (self.mesgfrom, self.mesgto, self.message)

class AprsStation:
   maxstatus = 4

   def __init__(self):
      self.call = ""           # callsign-SSID
      self.v = vector.Vector() # 
      self.p = 0               #
      self.h = 0               #
      self.g = 0               #
      self.d = 0               #
      self.micemsg = ""        #
      self.source = []         #"", "RMC", "GGA", "GLL", "Other", "MicE", "Posit", "Object", etc
      self.symprimary = 0      # boolean
      self.symidx = 0          # int index into symbol list
      self.symoverlay = ""     # char overlay if any
      self.status = []         # arbitrary status text, last few
      self.extra = ""          # formatted extra info I've gleaned (from NMEA sentences, for ex)

      self.where = waypoint.Waypoint()

      self.wxvalid = 0         # has wx stuff been saved?
      
      self.gust = 0            # wind gust (peak wind speed in mph over last 5 min)
      self.temperature = ""    # temperature (deg F...can also be -00 -> -99)
      self.rain = [0, 0, 0]    # [0] rainfall in last hour (hundredths of an inch)
                               # [1] rainfall since midnight (hundredths of an inch)
                               # [2] rainfall in last 24 hours (hundredths of an inch)
      self.humidity = 0        # humidity in % (00 = 100%)
      self.barometer = 0       # pressure (tenths of millibars/tenths of hPascal)
      self.luminosity = 0      # luminosity (watts per sq meter)
      self.snow = 0            # snowfall in last 24 hours (inches)
      self.rawrain = 0         # raw rain counter

      #timing stuff
      self.lastmoved = 0
      self.lastpacket = 0

   def Touch(self): self.lastpacket = time.time()
   def TouchMoved(self): self.Touch(); self.lastmoved = time.time()

   #different ways of setting symbol
   def SetSymSlash(self, symtab, sym):
      if symtab[0] == '/':
         self.symprimary = 1
      else:
         self.symprimary = 0
      self.symidx = ord(sym[0]) - ord('!') + 1

      if self.symprimary:
         self.symoverlay = ""
      else:
         if symtab[0] == '\\':
            self.symoverlay = ""
         else:
            self.symoverlay = symtab

   def SetSymCall(self, call):
      if len(call) == 6 and (call[0:4] == "GPSC" or call[0:4] == "GPSE"):
         if call[3] == 'C': self.symprimary = 1
         elif call[3] == 'E': self.symprimary = 0
         elif self.aprsdebug > 1: print "aprs> SetSymCall unknown sym format GPS[CE]nn"
         self.overlay = "" 
         sym = getint(call[4:6])

      elif len(call) >= 5 and call[0:3] == "GPS":
         try:
            self.symidx = GPSPriSymLookup.index(call[3:5])
            self.symprimary = 1
         except ValueError:
            try:
               self.symidx = GPSAltSymLookup.index(call[3:5])
               self.symprimary = 0
            except ValueError:
               if self.aprsdebug > 1: print "aprs> SetSymCall can't lookup %s" % call

         if len(call) == 6: self.symoverlay = call[5]
         else: self.symoverlay = ""

      else: 
         "aprs> couldn't parse sym from call %s" % call

   def GetSym(self):
      if self.symprimary:
         s = prisymtab[self.symidx]
      else:
         s = altsymtab[self.symidx]
      if len(self.symoverlay):
         s += " " + self.symoverlay
      return s

   def SetSymWX(self):
      symprimary = 1
      sym = 63

   def SetStatus(self, statin):
      s = statin #copy.deepcopy(statin)
      if s not in self.status:
         self.status.insert(0, s)
      while len(self.status) > self.maxstatus:
         self.status.pop()

   def SetSource(self, source):
      if not source in self.source: self.source.append(source)

   def HavePHG(self):
      return self.p or self.h or self.g

   def GetPHGStr(self):
      return "%3dW %4d' %1ddB" % (self.p, self.h, self.g)

   def GetAgeStr(self):
      age = int(time.time() - self.lastpacket)
      h = age/3600
      age -= h*3600
      m = age/60
      age -= m*60
      s = age

      if h == 0 and m == 0:
         agestr = "%2ds" % s
      elif h == 0:
         agestr = "%2dm" % m
      else:
         agestr = "%2dh" % h
      return agestr

   def GetAgeStrLong(self):
      age = int(time.time() - self.lastpacket)
      h = age/3600
      age -= h*3600
      m = age/60
      age -= m*60
      s = age

      if h == 0 and m == 0:
         agestr = "   %2ds" % s
      elif h == 0:
         agestr = "%2d:%02ds" % (m, s)
      else:
         agestr = "%2dh:%02dm" % (h, m)
      return agestr

   def IsDigi(self):
      return self.symidx == 3 or (not self.symprimary and (self.symidx == 63 or self.symidx == 73))

   def IsWX(self):
      if self.symidx == 63:
         return 1
      else:
         return 0



class Aprs(threading.Thread):
   def __init__(self, tnc, db):
      threading.Thread.__init__(self)
      self.db = db
      self.tnc = tnc
      self.running = 0
      self.aprsdebug = 1

      #for smartbeaconing
      self.lasttxtime = time.time()
      self.lasttxcourse = 0

      self.Initdbobjects()
      self.unackdpackets = []
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

   def Initdbobjects(self):
      """Set up any stat db objects we're going to be updating"""
# these are now initialized in config.py
#      self.db.Put("aprs/stations", {})
#      self.db.Put("aprs/messages", {})
      self.db.Put("aprs/beaconnow", 0)
      self.db.Put("aprs/msg", "")
      self.db.Put("aprs/mymesgids", {})

   def run(self):
      print "aprs> running"
      
      self.stations = self.db.Get("aprs/stations")
      self.packettypes = string.split("/ @ ! = $ > _ \\ `")
      self.messages = self.db.Get("aprs/messages")
      self.mymesgids = self.db.Get("aprs/mymesgids")

      data = ""
      i = 1
      while self.running:
         if i % 4 == 0:
            self.MaybeTx(self.db.Get("aprs/beaconnow"))
         elif i % 4 == 1:
            if len(self.unackdpackets):
               now = time.time()
               # cycle through the packets in unackdpackets
               #   if it's been at least 30 seconds since last tx and < 5 tx times,
               #      tx the packet
               #      increment packet.txtimes by 1
               # does this need to be on its own thread and just sleep a lot?
               pass
         elif i % 4 == 2:
            # kglueckFIX
            # this aprs/msg really should be a queue...for now this will suffice for now
            msg = self.db.Get("aprs/msg")
            if len(msg):
               self.db.Put("aprs/msg","")
               # decode supplied msg
               m = AprsMessage()
               m.mesgfrom = self.db.Get("config/tnc/mycall")
               m.type = '>'
               try:
                  if msg[0] == ':':
                     n = msg.find(':',1)
                     m.mesgto = msg[1:n]
                     p = msg.find('{')
                     if p > -1:
                        m.mesgid = msg[p+1:]
                        m.message = msg[n+1:p]
                        self.mymesgids[m.mesgid] = m.GetKey()
                     else:
                        m.mesgid = ''
                        m.message = msg[n+1:]
                  m.Touch()
                  self.messages[m.GetKey()] = m
               except IndexError:
                  pass
               # blindly send the preformatted message and trust the user
               # knew what they were doing when they manually assembled it!
               self.TxMesg(msg)

         while self.tnc.HavePackets():
            self.DispatchPacket(self.tnc.GetPacket())

         i += 1
         time.sleep(.1)
      print "aprs> exiting..."

   def MaybeTx(self, beaconnow):
      if self.db.Get("config/aprs/tx/enable"):
         vec = self.db.Get("gps/vector")
         speed = vec.speed_mph
         course = vec.course
   
         peg = 0
         now = time.time()
         sincelast = now - self.lasttxtime

         fast_speed = self.db.Get("config/aprs/tx/fast_speed")
         fast_rate =  self.db.Get("config/aprs/tx/fast_rate")
         slow_speed = self.db.Get("config/aprs/tx/slow_speed")
         slow_rate =  self.db.Get("config/aprs/tx/slow_rate")
         turn_angle = self.db.Get("config/aprs/tx/turn_angle")
         turn_slope = self.db.Get("config/aprs/tx/turn_slope")
         turn_time =  self.db.Get("config/aprs/tx/turn_time")

         if speed < slow_speed:
            rate = slow_rate
         else:
            if speed > fast_speed:
               rate = fast_rate
            else:
               rate = int(float(fast_rate) * float(fast_speed) / speed)

            headingchange = units.HeadingDiff(course, self.lasttxcourse) 
            turn_thresh = float(turn_angle) + float(turn_slope) / speed
            if headingchange > turn_thresh and sincelast > turn_time:
               peg = 1
   
         if sincelast > rate or peg or beaconnow:     # then TX
            #build packet
            packet = tnc.AX25Packet()
            packet.frm = self.db.Get("config/tnc/mycall") #"AD6XL-1"
            packet.to = self.db.Get("config/tnc/unproto") #APZ242"
            packet.repeaters = self.db.Get("config/tnc/path").split(",")
            status = self.db.Get("config/aprs/stat")
            symtab = self.db.Get("config/aprs/symtab")
            sym = self.db.Get("config/aprs/sym")
            here = self.db.Get("gps/pos/here")
   
            packet.data = "!%s%s%s%s%03d/%03d/A=%06d %s" %  (here.GetLatAPRS(), symtab, here.GetLonAPRS(), sym, 
               course, vec.speed_kn, here.alt_f, status)
   
            self.tnc.SendPacket(copy.copy(packet))
            if self.db.Get("config/aprs/injectme"):
               self.tnc.InjectRX(copy.copy(packet))
            
            self.lasttxtime = now
            self.lasttxcourse = course
            if beaconnow:
               self.db.Put("aprs/beaconnow", 0)

   def TxMesg(self, payload):
      if self.db.Get("config/aprs/tx/enable"):
         packet = tnc.AX25Packet()
         packet.frm = self.db.Get("config/tnc/mycall") #"AD6XL-1"
         packet.to = self.db.Get("config/tnc/unproto") #APZ242"
         packet.repeaters = self.db.Get("config/tnc/path").split(",")
         packet.data = payload
         self.unackdpackets.append(copy.copy(packet))
         self.tnc.SendPacket(packet)


   def DispatchPacket(self, packet):
      print "aprs> %s" % packet

      data = packet.data
      if len(data) < 1: return
      
      type = data[0]

      if type == ":": #is a message
         self.ParseMesg(packet)
         if self.aprsdebug > 1: print
      elif type == "}":  #is a third party packet...decode and reprocess payload
         newpacket = tnc.AX25Packet()

         n = data.find('>')
         if n > -1:
            newpacket.frm = data[1:n].replace(' ','')
            data = data[n+1:]
            n = data.find(':')
            if n > -1:
               c = data.find(',')
               if c > -1:
                  newpacket.to = data[:c]
                  data = data[c+1:]
               else:
                  if self.aprsdebug: print "aprs> failed decode of third party packet.to"
               newpacket.repeaters = data[:n]
               data = data[n+1:]
               newpacket.data = data
               self.DispatchPacket(newpacket)
            else:
               if self.aprsdebug: print "aprs> failed decode of third party packet"
         else:
            if self.aprsdebug:
               print "aprs> failed decode of third party packet"
               print

      else: # all other packet types
         self.ParseOther(packet)


      if self.aprsdebug > 1:
         if self.stations.has_key(packet.frm):
            self.PrintStation(self.stations[packet.frm])


   def ParseMesg(self, packet):
      # get message payload minus starting : in this format:
      # N5TLT-12 :blah blah blah blah (up to 67 characters){xxxxx
      # {xxxxx is optional
      data = packet.data[1:]
      n = data.find(':') 
      if n > -1:
         mycall = self.db.Get("config/tnc/mycall")
         m = AprsMessage()
         m.mesgto = data[0:n].replace(' ','')
         m.mesgfrom = packet.frm
         data = data[n+1:]
         #get optional mesgid
         n = data.find('{')
         if n > -1:
            m.mesgid = data[n+1:]
            data = data[:n]
         m.message = data

         mnew = 1
         mhash = m.GetKey()
         if self.messages.has_key(mhash) and self.messages[mhash].mesgto == m.mesgto:
            del m
            m = self.messages[mhash]
            mnew = 0

         m.Touch()
         if m.message[0:3] == "ack" and 3 < len(m.message) < 9 and m.mesgto == mycall:
            # it's an ack message, let's handle it if it and ack for a
            # message we sent.  otherwise, let's just ignore it...
            # kglueckFIX for now we ignore...
            ackid = m.message[3:]
            if self.mymesgids.has_key(ackid):
               self.messages[self.mymesgids[ackid]].Ack()
            elif self.aprsdebug:
               print "aprs/msg> unknown ack recvd: %s" % m.message.replace(' ','')
               self.messages[m.GetKey()] = m
         elif m.mesgto[3:6] == "FWD" or m.mesgto[0:3] == "BLN" or m.mesgto[0:4] == "NWS-" or m.mesgto == mycall or m.mesgfrom == mycall:
            if m.mesgto[0:3] == "BLN":
               m.type = 'b'
            elif m.mesgto[0:4] == "NWS-":
               m.type = 'w'
            elif m.mesgto == mycall:
               m.type = '<'
            elif m.mesgfrom == mycall:
               m.type = '>'

            # if it's a message to us, let's see if we need to respond
            if m.mesgto == mycall and m.message[0:5] == "?APRS":
               # send unack'd/undelivered messages to calling station
               if m.message[5] == "M":
                  pass
               elif m.message[5] == "P": # send POS in response
                  self.db.Put("aprs/beaconnow",1)
               elif m.message[5] == "S": # send station status in response
                  self.TxMesg(">Mobile Linux! www.loopfree.net/xlaprs/")
               elif m.message[5] == "T": # send trace in response
                  #Example message payload :N5TLT-12 :N5TLT-12>APZ242,W5AC-2,WIDE2-2:
                  pass

            if mnew: self.messages[m.GetKey()] = m
            if len(m.mesgid) and m.mesgto == mycall:  # and not m.acked
               m.Ack()
               self.TxMesg(m.GetAckStr())
               self.TxMesg(m.GetAckStr())
            if self.aprsdebug: print "aprs/msg> ", m, "%%", m.GetKey()
      else:
         if self.aprsdebug: print "aprs/msg> ParseMesg() failed with bad payload data"
      # else we just return as the message ain't for us!

   def ParseOther(self, packet):
      data = packet.data
      if len(data) < 1: return
      type = data[0]

      # make ID/Beacon packets into APRS status message packets
      if (packet.to == "BEACON" or packet.to == "ID") and type not in self.packettypes:
         data = ">" + data

      if self.stations.has_key(packet.frm):
         s = self.stations[packet.frm]
      else:
         s = AprsStation()
         s.call = packet.frm
         self.stations[s.call] = s

      s.Touch()

      # big try loop around data to catch IndexErrors where we reference
      # something that's not there as someone sent something non-standard
      try:

      # / position w/timestamp
      # @ position w/timestamp w/out messaging
      # ! position w/out timestamp w/out messaging (or ultimeter WX)
      # = position w/out timestampt w/ messaging
      # _ weather report w/o position report

      # !3411.53NN11642.57W#PHG4330/Onyx Peak - www.cal-net.org
      # _10010915c059s003g007t080r000p031P000h76b10151wU2K
      # !!0000008002C7000027940310--------0119023000000000
      # $ULTW0091003202EA00452783FFFF8B8C000103E8011A023000170035

         if type[0] == '!' and data[1] == '!':
            self.DecodeUltimeter(s, data[2:])

         elif type == '!' or type == '=' or type == '/' or type =='@':
            if type == '/' or type == '@':
               #need to parse timestamp?
               data = data[7:]

            s.where.SetPos(data[1:9], data[10:19])
            s.SetSymSlash(data[9], data[19])
            s.SetSource("Posit")

            #chop and keep going
            data = data[20:]

            #have seen lower case "PHG" in wild, too. Valid? Hmmm...
            phgdidx = data.find("PHG")
            if phgdidx >= 0:
               s.p = PHGDpower[getint(data[phgdidx + 3])]
               s.h = PHGDheight[getint(data[phgdidx + 4])]
               s.g = getint(data[phgdidx + 5])
               s.d = PHGDdirectivity[getint(data[phgdidx + 6])]
               data = data[0:phgdidx] + data[phgdidx+7:]

            # CSE/SPD or WindDIR/SPD (assume correct position in string)
            restWX = 0
            if len(data) > 6:
               if data[3] == "/":
                  s.v.course = getint(data[0:3])
                  if s.IsWX():
                     restWX = 1
                     s.v.speed_mph = getint(data[4:7])
                  else:
                     s.v.speed_kn = getint(data[4:7])
                  data = data[7:]

            #/A=001866
            altidx = data.find("/A=")
            if altidx >= 0:
               s.where.alt_f = getint(data[altidx+3 : altidx+9])
               data = data[0:altidx] + data[altidx+9:]

            if restWX:
               # parse out WX crap that we have determined rest of packet to be
               self.DecodeGenericWX(s,data)

            else: #otherwise rest of data is status
               slashidx = data.find('/')
               if slashidx >= 0 and slashidx < 4: data = data.replace('/', ' ')
               status = data.strip()
               if len(status) > 0: s.SetStatus(status)

         #
         # $ raw NMEA or Ultimeter WX
         #
         elif type == '$':
            if data[0:5] == "$ULTW":  #Ultimeter!
               self.DecodeUltimeter(s, data[5:])

            elif data[0:6] == "$GPRMC":
               toks = string.split(data, ",")
               if toks[2][0] == "A":
                  valid = 1
               else:
                  valid = 0
               if valid:
                  latdeg = getint(toks[3][0:2])
                  latmin = getfloat(toks[3][2:8])
                  if toks[4] == "S": latdeg = -latdeg

                  londeg = getint(toks[5][0:3])
                  lonmin = getfloat(toks[5][3:9])
                  if toks[6] == "W": londeg = -londeg

                  s.where.SetPos((latdeg, latmin), (londeg, lonmin))
                  s.v.speed_kn = getfloat(toks[7])
                  s.v.course = getfloat(toks[8])

                  s.SetSource("RMC")

            elif data[0:6] == "$GPGGA":
               toks = string.split(data, ",")
               valid = getint(toks[6][0])
               if valid > 0:
                  latdeg = getint(toks[2][0:2])
                  latmin = getfloat(toks[2][2:8])
                  if toks[3] == "S": latdeg = -latdeg

                  londeg = getint(toks[4][0:3])
                  lonmin = getfloat(toks[4][3:9])
                  if toks[5] == "W": londeg = -londeg

                  s.where.SetPos((latdeg, latmin), (londeg, lonmin))
                  s.where.alt_m = getfloat(toks[9])

                  s.SetSource("GGA")
                  # valid=2 -> differential fix
                  tracking = getint(toks[7])
#                  s.extra = ...
                  
            elif data[0:6] == "$GPGLL":
               toks = string.split(data, ",")
               if toks[6][0] == "A":
                  latdeg = getint(toks[1][0:2])
                  latmin = getfloat(toks[1][2:8])
                  if toks[2] == "S": latdeg = -latdeg

                  londeg = getint(toks[3][0:3])
                  lonmin = getfloat(toks[3][3:9])
                  if toks[4] == "W": londeg = -londeg

                  s.where.SetPos((latdeg, latmin), (londeg, lonmin))
                  s.SetSource("GLL")

            elif data[0:6] == "$GPVTG":
               toks = string.split(data, ",")
               s.v.speed_kn = getfloat(toks[5])
               s.v.course = getfloat(toks[1])
               s.SetSource("VTG")

            elif data[0:6] == "$GPWPT": #recommended in APRS spec.. huh?
               pass
         
            s.SetSymCall(packet.to)
         

         #
         # \ kenwood mic-e
         # ` regular mic-e
         #
         elif type == "'" or type == '`':
            ord0 = ord('0')
            ordc = ord('c')
            #
            #Get latitude/mes/ns/ew/longoffset from AX25 destination
            #
            if len(packet.to) < 6:
               return
            lat = list("0000.00")
            lat[0] = MicEDest[ord(packet.to[0]) - ord0][0]
            lat[1] = MicEDest[ord(packet.to[1]) - ord0][0]
            lat[2] = MicEDest[ord(packet.to[2]) - ord0][0]
            lat[3] = MicEDest[ord(packet.to[3]) - ord0][0]
            lat[4] = '.'
            lat[5] = MicEDest[ord(packet.to[4]) - ord0][0]
            lat[6] = MicEDest[ord(packet.to[5]) - ord0][0]
            lat = "".join(lat)

            msg = 0
            #/msg is custom if any msg bits are encoded custom
            if MicEDest[ord(packet.to[0]) - ord0][1] == 'c': msg |= 0x8
            if MicEDest[ord(packet.to[1]) - ord0][1] == 'c': msg |= 0x8
            if MicEDest[ord(packet.to[2]) - ord0][1] == 'c': msg |= 0x8

            if MicEDest[ord(packet.to[0]) - ord0][1] != '0': msg |= 0x4
            if MicEDest[ord(packet.to[1]) - ord0][1] != '0': msg |= 0x2
            if MicEDest[ord(packet.to[2]) - ord0][1] != '0': msg |= 0x1

            s.micemsg = MicEMessages[msg]
         
            ns =         MicEDest[ord(packet.to[3]) - ord0][2]
            lonoffset = (ord(MicEDest[ord(packet.to[4]) - ord0][3]) - ord0) * 100
            ew =         MicEDest[ord(packet.to[5]) - ord0][4]

            lat += ns
            
            #
            #Get lon/speed/course/symbol/status text from AX25 information field
            #

            londeg = ord(data[1]) - 28 + lonoffset
            if londeg >= 180 and londeg <= 189: londeg -= 80
            elif londeg >= 190 and londeg <= 199: londeg -= 190
         
            lonmin = ord(data[2]) - 28
            if lonmin >= 60: lonmin -= 60

            lonfrac = ord(data[3]) - 28

            lon =  londeg * 100.0
            lon += lonmin + lonfrac / 100.0
#            lon = ew == 'W' ? -lon : lon

            s.where.SetPos(lat, "%08.2f%s" % (lon, ew))

            speed   = (ord(data[4]) - 28) * 10
            speed  += (ord(data[5]) - 28) / 10
            course  = ((ord(data[5]) - 28) % 10) * 100
            course += (ord(data[6]) - 28)

            if speed >= 800: speed -= 800
            if course >= 400: course -= 400

            s.v.speed_kn = speed
            s.v.course = course

            s.SetSymSlash(data[8], data[7])

            #
            #Now do mic-e status text parsing at data[9]
            #

            if len(data) > 9:
               if data[9] == "'" or data[9] == '`' or data[9] == ',':
                  #mic-e telemetry data instead of status text 
                  pass
               else:
                  status = data[9:]
   
                  #Look for mic-e altitude format
                  i = status.find('}')
                  if i >= 0:
                     alt = 0.0
                     alt  = (ord(status[i-3]) - ord('!')) * 91 * 91
                     alt += (ord(status[i-2]) - ord('!')) * 91
                     alt += (ord(status[i-1]) - ord('!'))
                     alt -= 10000  #relative to 10km below sea level
   
                     s.where.alt_m = alt
                     status = status[:i-3] + status[i+1:] #delete out of status text
               
                  #Look for out-of spec altitude format
                  #ui = status.StrStr_ui("/A=");
                  #if (ui != UINT_MAX) {
                  #   rS.where.altitude = strtol(status.Base_sz() + ui + 3, NULL, 10);
                  #   status.Delete_v(ui, ui + 8); //delete out of status text
                  #   printf("parse> non-std altitude: %f\n", rS.where.altitude);
                  #}
   
                  #Look for kenwood d700/d7 flags and make them readable
                  if len(status) and status[0] == ']':
                     status = "TM-D700 " + status[1:]
                  elif len(status) and status[0] == '>':
                     status = "TH-D7 " + status[1:]
   
                  s.SetStatus(status)

            s.SetSource("MicE")
         
         elif type == '>':
            if len(data) > 1:
               s.SetStatus(data[1:])

         elif type == '_':
            self.DecodeGenericWX(s,data)

      except IndexError:      
         print "aprs> malformed packet payload data"


   def DecodeGenericWX(self, s, wxdata):

      s.SetSource("WX")
      s.SetSymWX()

      n = wxdata.find("c")
      if n > -1: s.v.course = getint(wxdata[n+1:n+4])

      n = wxdata.find("s")
      if n > -1: s.v.speed_mph = getint(wxdata[n+1:n+4])

      n = wxdata.find("g")
      if n > -1: s.gust = getint(wxdata[n+1:n+4])

      n = wxdata.find("t")
      if n > -1: s.temperature = getint(wxdata[n+1:n+4])

      rain = 0.0
      rain24 = 0.0
      rainmid = 0.0
      r = wxdata.find("r")
      p = wxdata.find("p")
      P = wxdata.find("P")
      if r > -1: rain = getint(wxdata[r+1:r+4]) / 100.0
      if r > -1: rain24 = getint(wxdata[p+1:p+4]) / 100.0
      if r > -1: rainmid = getint(wxdata[P+1:P+4]) / 100.0
      s.rain = [rain, rainmid, rain24]

      n = wxdata.find("h")
      if n > -1:
         h = wxdata[n+1:n+3]
         if h == "00":
            s.humidity = 100
         else:
            s.humidity = getint(h)

      n = wxdata.find("b")
      if n > -1: s.barometer = getint(wxdata[n+1:n+6]) / 10.0

      blum = 0
      llum = 0
      L = wxdata.find("L")
      l = wxdata.find("l")
      if L > -1: blum = getint(wxdata[L+1:L+4])
      if l > -1: llum = getint(wxdata[l+1:l+4])
      s.luminosity = llum + (blum * 1000)

      # check this tag...S is not correct...
      #n = wxdata.find("S")
      #if n > -1: s.snow = wxdata[n+1:n+4]

      #n = wxdata.find("#")
      #if n > -1: s.rawrain = wxdata[n+1:n+4]

      #look into using timing to show data updates in time
      s.wxvalid = 1


   def DecodeUltimeter(self, s, data):
      s.SetSource("Ultimeter")
      s.SetSymWX()

      # 0000008002C7000027940310--------0119023000000000
      # 0091003202EA00452783FFFF8B8C000103E8011A023000170035

      s.gust = units.km2mi(getint(data[0:4],16) / 10.0)
      s.v.course = getint(data[6:8],16)
      s.temperature = getint(data[8:12],16) / 10.0
      s.rain[2] = getint(data[12:16],16) / 100.0
      s.barometer = getint(data[16:20],16) / 10.0
      s.humidity = getint(data[32:36],16) / 10.0
      s.rain[1] = getint(data[44:48],16) / 100.0
      s.v.speed_mph = units.km2mi(getint(data[48:52],16) / 10.0)
      s.wxvalid = 1



   def PrintStation(self, s):
      here = self.db.Get("gps/pos/here")
      if s.v.speed_mph:
         print "aprs> %s (%s) is at: %s heading %3.1f at %3.1fmph" % (s.call, s.GetSym(), s.where,s.v.course,s.v.speed_mph)
      else:
         print "aprs> %s (%s) is at: %s" % (s.call, s.GetSym(), s.where)

      if s.p or s.h or s.d:
         print "aprs> power: %dW height: %d\' gain:%ddb direc:%d" % (s.p, s.h, s.g, s.d)

      if s.where.Valid():
         print "aprs> dist %4.2fmi  bearing %s (%3.1f)" %  (here.DistanceTo(s.where), units.CompassOrd3(here.BearingTo(s.where)), here.BearingTo(s.where))

      if s.wxvalid:
         print "aprs> wind from: %d (%s) at %dmph gust: %d temp: %s" % (s.v.course, units.CompassOrd3(s.v.course),
                                                                           s.v.speed_mph, s.gust,s.temperature)
         print "aprs> rain (1 hr: %1.2f, since midnt: %1.2f, 24 hr: %1.2f)" % (s.rain[0],s.rain[1],s.rain[2])
         print "aprs> baro: %04.1fmbar  humidity: %3.1f%%" % (s.barometer,s.humidity)

#       if len(s.source):
#          print "aprs> source: %s" % string.join(s.source, " ")

      if len(s.micemsg):
         print "aprs> micemsg: %s" % s.micemsg

      for line in s.status:
         if len(line):
            print "aprs> status: '%s'" % line
      print


def getint(s, base=10):
   try:
      return int(s,base)
   except:
      return 0

def getfloat(s):
   try:
      return float(s)
   except:
      return 0.0


# static data
prisymtab = [
   "NoSym",       #00
   "Police",      #01
   "Reserved",    #02
   "Digi",        #03
   "Phone",       #04
   "DX",          #05
   "HF Gate",     #06
   "Aircraft",    #07
   "Mobile Sat",  #08
   "",            #09
   "Snowmobile",  #10
   "Red Cross",   #11
   "Boy Scouts",  #12
   "House",       #13
   "X",           #14
   "*", #dot      #15
   "(0)",         #16
   "(1)",         #17
   "(2)",         #18
   "(3)",         #19
   "(4)",         #20
   "(5)",         #21
   "(6)",         #22
   "(7)",         #23
   "(8)",         #24
   "(9)",         #25
   "Fire",        #26
   "Campground",  #27
   "Motorcycle",  #28
   "Railroad",    #29
   "Car",         #30    
   "Server",      #31
   "Hurricane",   #32
   "Aid Statn.",  #33
   "BBS",         #34
   "Canoe",       #35
   "",            #36
   "Eyeball",     #37
   "",            #38
   "Grid Sq.",    #39
   "Hotel",       #40    
   "TCP/IP",      #41
   "",            #42
   "School",      #43
   "",            #44
   "MacAPRS",     #45
   "NTS Stn.",    #46
   "Balloon",     #47
   "Police",      #48
   "",            #49
   "RV",          #50    
   "Space Shtl",  #51
   "SSTV",        #52
   "Bus",         #53
   "ATV",         #54
   "NWS Site",    #55
   "Helicopter",  #56
   "Sailboat",    #57
   "WinAPRS",     #58
   "Jogger",      #59
   "Triangle",    #60    
   "PBBS",        #61
   "Aircraft",    #62
   "WX",          #63
   "Dish",        #64
   "Ambulance",   #65
   "Bicycle",     #66
   "",            #67
   "Fire Dept",   #68
   "Horse",       #69
   "Fire Truck",  #70    
   "Glider",      #71
   "Hospital",    #72
   "IOTA",        #73
   "Jeep",        #74
   "Truck",       #75
   "",            #76
   "Mic-rptr",    #77
   "Node",        #78
   "EOC",         #79
   "Rover",       #80    
   "Grid Sq.",    #81
   "Antenna",     #82
   "Boat",        #83
   "Truck Stop",  #84
   "Bigrig",      #85
   "Van",         #86
   "Water Stn",   #87
   "XAPRS",       #88
   "House+Yagi",  #89
   "",            #90
   "",            #91
   "Reserved",    #92
   "",            #93
   "Reserved"     #94
   ]

altsymtab = [
   "NoSym",       #00
   "Emergency",   #01
   "Reserved",    #02
   "Digi",        #03
   "Bank/ATM",    #04
   "",            #05
   "HF Gate",     #06
   "Crash",       #07
   "Cloudy",      #08
   "",            #09
   "Snow",        #10
   "Church",      #11
   "Girl Scts",   #12
   "House HF",    #13
   "Unknown",     #14
   "",            #15
   "(*)",         #16
   "",            #17
   "",            #18
   "",            #19
   "",            #20
   "",            #21
   "",            #22
   "",            #23
   "",            #24
   "Gas Stn.",    #25
   "Hail",        #26
   "Park",        #27
   "NWS Advs.",   #28
   "",            #29
   "Car",         #30    
   "Info",        #31
   "Hurricane",   #32
   "[]",          #33
   "BlowSnow",    #34
   "CoastGuard",  #35
   "Drizzle",     #36
   "Smoke",       #37
   "Frz Rain",    #38
   "SnowShower",  #39
   "Haze",        #40    
   "RainShower",  #41
   "Lightning",   #42
   "Kenwood",     #43
   "LightHouse",  #44
   "",            #45
   "Nav Buoy",    #46
   "",            #47
   "Parking",     #48
   "Earthquake",  #49
   "Restaurant",  #50    
   "Satellite",   #51
   "T-Storm",     #52
   "Sunny",       #53
   "VORTAC",      #54
   "NWS Site",    #55
   "Pharmacy",    #56
   "",            #57
   "",            #58
   "Wall Cloud",  #59
   "",            #60    
   "",            #61
   "Aircraft",    #62
   "WX Digi",     #63
   "Rain",        #64
   "",            #65
   "Blowing",     #66
   "RACES",       #67
   "DX Spot",     #68
   "Sleet",       #69
   "Funnel Cld",  #70    
   "Gale",        #71
   "Ham Store",   #72
   "Sm Digi",     #73
   "Work Zone",   #74
   "",            #75
   "Area",        #76
   "",            #77
   "/_\\",        #78
   "o",           #79
   "Prtl Cldy",   #80    
   "",            #81
   "Restrooms",  #82
   "Ship",        #83
   "Tornado",     #84
   "Truck",       #85
   "Van",         #86
   "Flooding",    #87
   "",            #88
   "",            #89
   "",            #90
   "Fog",         #91
   "Reserved",    #92
   "",            #93
   "Reserved"    #94
]


GPSPriSymLookup = [
"", "BB", "BC", "BD", "BE", "BF", "BG", "BH", "BI", "BJ", "BK",     #0-10
    "BL", "BM", "BN", "BO", "BP", "P0", "P1", "P2", "P3", "P4",     #11-20
    "P5", "P6", "P7", "P8", "P9", "MR", "MS", "MT", "MU", "MV",     #21-30
    "MW", "MX", "PA", "PB", "PC", "PD", "PE", "PF", "PG", "PH",     #31-40
    "PI", "PJ", "PK", "PL", "PM", "PN", "PO", "PP", "PQ", "PR",     #41-50
    "PS", "PT", "PU", "PV", "PW", "PX", "PY", "PZ", "HS", "HT",     #51-60
    "HU", "HV", "HW", "HX", "LA", "LB", "LC", "LD", "LE", "LF",     #61-70
    "LG", "LH", "LI", "LJ", "LK", "LL", "LM", "LN", "LO", "LP",     #71-80
    "LQ", "LR", "LS", "LT", "LU", "LV", "LW", "LX", "LY", "LZ",     #81-90
    "J1", "J2", "J3", "J4"                                          #91-94
]

GPSAltSymLookup = [
"", "OB", "OC", "OD", "OE", "OF", "OG", "OH", "OI", "OJ", "OK",     #0-10
    "OL", "OM", "ON", "OO", "OP", "A0", "A1", "A2", "A3", "A4",     #11-20
    "A5", "A6", "A7", "A8", "A9", "NR", "NS", "NT", "NU", "NV",     #21-30
    "NW", "NX", "AA", "AB", "AC", "AD", "AE", "AF", "AG", "AH",     #31-40
    "AI", "AJ", "AK", "AL", "AM", "AN", "AO", "AP", "AQ", "AR",     #41-50
    "AS", "AT", "AU", "AV", "AW", "AX", "AY", "AZ", "DS", "DT",     #51-60
    "DU", "DV", "DW", "DX", "SA", "SB", "SC", "SD", "SE", "SF",     #61-70
    "SG", "SH", "SI", "SJ", "SK", "SL", "SM", "SN", "SO", "SP",     #71-80
    "SQ", "SR", "SS", "ST", "SU", "SV", "SW", "SX", "SY", "SZ",     #81-90
    "Q1", "Q2", "Q3", "Q4"                                          #91-94
]


PHGDpower = [0, 1, 4, 9, 16, 25, 36, 40, 64, 81]
PHGDheight = [10, 20, 40, 80, 160, 320, 640, 1280, 2560, 5120]
PHGDdirectivity = [0, 45, 90, 135, 180, 225, 270, 315, 360, 0]

MicEDest = [
   "00S0E",            # 0 [0]
   "10S0E",            # 1
   "20S0E",            # 2
   "30S0E",            # 3
   "40S0E",            # 4
   "50S0E",            # 5 [5]
   "60S0E",            # 6
   "70S0E",            # 7
   "80S0E",            # 8
   "90S0E",            # 9
   "-----",            #   [10]
   "-----", 
   "-----", 
   "-----", 
   "-----", 
   "-----",            #   [15]
   "-----", 
   "0c---",            # A
   "1c---",            # B
   "2c---",            # C
   "3c---",            # D [20]
   "4c---",            # E
   "5c---",            # F
   "6c---",            # G
   "7c---",            # H
   "8c---",            # I [25]
   "9c---",            # J
   "0c---",            # K
   "00S0E",            # L
   "-----",
   "-----",            #   [30]
   "-----",
   "0sN1W",            # P
   "1sN1W",            # Q
   "2sN1W",            # R
   "3sN1W",            # S [35]
   "4sN1W",            # T
   "5sN1W",            # U
   "6sN1W",            # V
   "7sN1W",            # W
   "8sN1W",            # X [40]
   "9sN1W",            # Y
   "0sN1W"             # Z
]

MicEMessages = [
   "Emergency",
   "Priority",
   "Special",
   "Committed",
   "Returning",
   "In Service",
   "Enroute",
   "Off Duty",
   "Emergency",
   "Custom 6",
   "Custom 5",
   "Custom 4",
   "Custom 3",
   "Custom 2",
   "Custom 1",
   "Custom 0"
]



class AprsCalc(threading.Thread):
   def __init__(self, db):
      threading.Thread.__init__(self)
      self.db = db
      self.running = 0
      self.Initdbobjects()
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

   def Initdbobjects(self):
      """Set up any stat db objects we're going to be updating"""
      self.db.Put("aprs/byalpha", [])
      self.db.Put("aprs/bydistance", [])
      self.db.Put("aprs/bytime", [])
      self.db.Put("aprs/byconfig", [])
      self.db.Put("aprs/messagelist", [])

   def run(self):
      print "aprscalc> running"
      
      self.stations = self.db.Get("aprs/stations")
      self.messages = self.db.Get("aprs/messages")

      i = 0
      statokill = []
      mestokill = []
      while self.running:
         sta = self.stations.keys()
         mes = self.messages.keys()
         for s in statokill:
            if s in sta:
               del sta[sta.index(s)]
         for m in mestokill:
            if m in mes:
               del mes[mes.index(m)]

         #grab common stuff from db
         here = self.db.Get("gps/pos/here")

         #calc byalpha
         a = copy.copy(sta)
         a.sort()
         self.db.Put("aprs/byalpha", a)

         #calc bytime
         t = []
         for call in sta:
            t.append((call, self.stations[call].lastpacket))
         t.sort(lambda a, b: (cmp(b[1],a[1])))
         self.db.Put("aprs/bytime", [pair[0] for pair in t])

         t = []
         for mhash in mes:
            t.append((mhash, self.messages[mhash].timestamp))
         t.sort(lambda a, b: (cmp(b[1],a[1])))
         self.db.Put("aprs/messagelist", [pair[0] for pair in t])
         self.messagelist = self.db.Get("aprs/messagelist")

         if i % 5 == 0:
            #calc bydistance
            d = []
            for call in sta:
               d.append((call, here.DistanceTo(self.stations[call].where)))
            d.sort(lambda a, b: (cmp(a[1],b[1])))
            self.db.Put("aprs/bydistance", [pair[0] for pair in d])

         if i % 5 == 1:
            #calc byheading
            course =  int(self.db.Get("gps/vector").course)
            c = []
            for call in sta:
               if self.stations[call].where.Valid():
                  bearingto = int(here.BearingTo(self.stations[call].where))
                  cross = units.HeadingDiff(course, bearingto)
                  c.append((call, cross))
            c.sort(lambda a, b: (cmp(a[1],b[1])))
            self.db.Put("aprs/bybearing", [pair[0] for pair in c])

         if i % 5 == 2:
            #mark old stations for deletion
            ntokill = []
            maxage = self.db.Get("config/aprs/maxage")
            oldlimit = time.time() - maxage
            for call in sta:
               if self.stations[call].lastpacket < oldlimit:
                  ntokill.append(call)

            #delete stations marked during last run
            for s in statokill:
               del self.stations[s]
            statokill = copy.copy(ntokill)

         if i % 60 == 7:
            #mark old messages for deletion
            ntokill = []
            maxmsgage = self.db.Get("config/aprs/maxmsgage")
            oldlimit = time.time() - maxmsgage
            for hash in mes:
               if self.messages[hash].timestamp < oldlimit:
                  ntokill.append(hash)

            #delete messages marked during last run
            for m in mestokill:
               del self.messages[m]
            mestokill = copy.copy(ntokill)

         if i % 60 == 11:
            #delete messages that bring our total over 60
            length = len(self.messages.keys())
            if length > 60:
               for i in range(length-1,59,-1):
                  del self.messages[self.messagelist[i]]
            

         #put filtered/processed list into db
         sorttype = self.db.Get("config/aprs/sort")
         filtertype = self.db.Get("config/aprs/filter")
         filterdist = self.db.Get("config/aprs/maxdist")
         showme = self.db.Get("config/aprs/showme")
         mycall = self.db.Get("config/tnc/mycall")
         calls = self.db.Get("aprs/by" + sorttype)

         # type filtering
         filteredcalls = []
         if filtertype == "all":
            calls = copy.copy(calls)
         elif filtertype == "digis":
            for call in calls:
               if self.db.Get("aprs/stations")[call].IsDigi():
                  filteredcalls.append(call)
            calls = copy.copy(filteredcalls)
         elif filtertype == "moving":
            for call in calls:
               if self.db.Get("aprs/stations")[call].v.IsMoving():
                  filteredcalls.append(call)
            calls = copy.copy(filteredcalls)
         elif filtertype == "wx":
            for call in calls:
               if self.db.Get("aprs/stations")[call].IsWX():
                  filteredcalls.append(call)
            calls = copy.copy(filteredcalls)

         # distance filtering
         filteredcalls = []
         if filterdist:
            for call in calls:
               if here.DistanceTo(self.db.Get("aprs/stations")[call].where) <= filterdist:
                  filteredcalls.append(call)
            calls = copy.copy(filteredcalls)

         # mycall filtering
         if not showme and mycall in calls:
            del calls[calls.index(mycall)]
   
         self.db.Put("aprs/byconfig", calls)


         i += 1
         time.sleep(1)

      print "aprscalc> exiting..."
