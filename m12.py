#!/usr/bin/python

import gps, serial, threading, time, string, units, waypoint, struct, vector

class M12(gps.Gps, threading.Thread):
   def __init__(self, port, db):
      threading.Thread.__init__(self)
      gps.Gps.__init__(self, db)
      self.port = port
      self.running = 0
      try:
         self.s = serial.Serial(port, 9600, rtscts=0, xonxoff=0, timeout=0)
      except:
         print "m12> could not open serial port %d" % self.port

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
      print "m12> running"
      data = ""

      self.Reset()

      while self.running:
         data = data + self.s.read(500)
         if string.find(data, "@@") >= 0:
            # split data into array of individual motorola sentences
            # all elements of lines are guaranteed to be length > 0
            lines = [l for l in data.split("@@") if len(l)]
            # if there is data lines and the last character of the last
            # line is not a newline then it is a partial sentence and
            # we want to put the unfinished sentence back so that the
            # next read will (hopefully) finish it...
            if len(lines) > 0 and lines[-1][-1] != "\n":
               data = "@@" + lines.pop()
            else:  # else we clear the way for new data to be read next time
               data = ""
            for line in lines:
               line = line.replace("\r\n", "")
               # compare the computed/given cksums, if good, send on to parser
               if Xsum(line[:-1]) == ord(line[-1]):
                  self.Parse(line)
                
         time.sleep(.2)
      print "m12> exiting..."
      self.s.close()

   def Send(self, command):
      self.s.write("@@" + command + chr(Xsum(command)) + "\r\n")

   def Reset(self):
#      self.Send("Cj")               #receiver ID
      self.Send("Ha\x01")           #gimme long position message
      self.Send("Bb\x01")           #gimme sat data

      self.Send("Aq\x03")           #turn on ionospheric/tropo correction
      self.Send("Ao\x31")           #select datum 49 (WGS-84)
      self.Send("AN\x50")           #setup velocity filter (0A = max, 64 = min)
      self.Send("AQ\x01")           #position filter on
      self.Send("Gc\x02")           #PPS only when tracking at least one sat

      self.prnSig = {}
      self.prnEl = {}
      self.prnAz = {}

   def Seteas(self):
      """Combine self.prn* into dict for db"""
      eas = {}
      for prn in self.prnAz.keys():
         if prn in self.prnEl and prn in self.prnSig:
            eas[prn] = {"el":self.prnEl[prn], "az":self.prnAz[prn], "sig":self.prnSig[prn]}
      self.db.Put("gps/sat/prn/eas", eas)

   def Parse(self, line):
#      print "m12> (%d) %s" % (len(line), line[:2])
      if line[:2] == "Ha":
         #time
         try:
            (mon, day, yr, hr, min, sec, secf) = struct.unpack(">BBHBBBI", line[2:13])
         except :
            print "m12> error unpacking date/time bytes"
            return
#         print "m12> %d/%d/%d %d:%d:%d:%d" % (mon, day, yr, hr, min, sec, secf)

         self.db.Put("gps/time/month", mon)
         self.db.Put("gps/time/day", day)
         self.db.Put("gps/time/year", yr)
         self.db.Put("gps/time/hour", hr)
         self.db.Put("gps/time/minute", min)
         self.db.Put("gps/time/second", sec)

         #filtered position
         try:
            (lat, lon, gpsalt, mslalt) = struct.unpack(">4i", line[13:29])
         except :
            print "m12> error unpacking lat/lon bytes"
            return
#         print "m12> lat %d lon %d gpsalt %d mslalt %d" % (lat, lon, gpsalt, mslalt)

         #unfiltered position
         try:
            (ulat, ulon, ugpsalt, umslalt) = struct.unpack(">4i", line[29:45])
         except :
            print "m12> error unpacking ulat/ulon/... bytes"
            return
#         print "m12> lat %d lon %d gpsalt %d mslalt %d" % (ulat, ulon, ugpsalt, umslalt)

         #speed, course
         try:
            (speed3, speed2, course) = struct.unpack(">3H", line[45:51])
         except :
            print "m12> error unpacking speed/course bytes"
            return
#         print "m12> speed3: %d speed2: %d course: %5.1f" % (speed3, speed2, course/10.0)
         self.db.Get("gps/vector").speed_ms = speed3 / 100.0
         self.db.Get("gps/vector").course = course / 10.0
         self.db.Get("gps/vvector").PutSample(gpsalt)

#         print "m12>  vec: %s" % self.db.Get("gps/vector")

         #dop, sat vis
         try :
            (dop, vis, track) = struct.unpack(">HBB", line[51:55])
         except :
            print "m12> error unpacking dop/vis/tracking bytes"
            return
#         print "m12> dop: %d  sats %d/%d" % (dop, track, vis)
         self.db.Put("gps/dop", dop/10.0)
         self.db.Put("gps/sat/tracking", track)
         self.db.Put("gps/sat/visible", vis)

         #channel status
         for i in range(55, 127, 6):
            try:
               (prn, mode, sig, iode, chanstat) = struct.unpack(">4BH", line[i:i+6])
            except:
               print "m12> error unpacking channel status bytes"
               return

#commented out to save CPU since we don't use this data for anything
            s = []
            if chanstat & 0x8000: pass #reserved
            if chanstat & 0x4000: pass #reserved
            if chanstat & 0x2000: pass #reserved
            if chanstat & 0x1000: pass #reserved
            if chanstat & 0x0800: s += ["time solution"]
            if chanstat & 0x0400: s += ["differential"]
            if chanstat & 0x0200: s += ["invalid"]
            if chanstat & 0x0100: s += ["parity error"]
            if chanstat & 0x0080: s += ["position solution"]
            if chanstat & 0x0040: s += ["momentum alert"]
            if chanstat & 0x0020: s += ["anti-spoof"]
            if chanstat & 0x0010: s += ["unhealthy"]
            if chanstat & 0x0008: pass #sat accuracy
            if chanstat & 0x0004: pass #sat accuracy
            if chanstat & 0x0002: pass #sat accuracy
            if chanstat & 0x0001: pass #sat accuracy

            if prn:
               self.prnSig[prn] = sig
#               print "m12> prn %2d mode %d sig %3d iode %3d chanstat %s" % (prn, mode, sig, iode, " ".join(s))

         #receiver status
         try:
            (recvstat, bias, osc, temp, utcparam, gmtsign, gmthour, gmtmin, id) = struct.unpack(">HxxhIhBBBB6s", line[127:149])
         except :
            print "m12> error unpacking recvstat bytes"
            return

         fix = ['', '', 'Bad Geometry', 'Acquiring', 'PosHold', 'Propagate', '2D', '3D'][(recvstat & 0xE000) >> 13]
         mymode = [0, 0, 0, 0, 0, 0, 2, 3][(recvstat & 0xE000) >> 13]

         if recvstat & 0x1000: pass #reserved
         if recvstat & 0x0800: pass #reserved
         if recvstat & 0x0400: pass #reserved
         fastacq      = recvstat & 0x0200
         filterreset  = recvstat & 0x0100
         cold         = recvstat & 0x0080
         differential = recvstat & 0x0040
         poslock      = recvstat & 0x0020
         survey       = recvstat & 0x0010
         badvis       = recvstat & 0x0008
         antok        = not (recvstat & 0x0004 or recvstat & 0x0002)
         codeloc      = recvstat & 0x0001
#         print "m12> fix %s bias %d osc %d temp %3.1f" % (fix, bias, osc, temp / 2.0)
#         print "m12> gpsalt: %4.2fft mslalt: %4.2fft" % (units.m2f(gpsalt / 100.0), units.m2f(mslalt / 100.0))

         self.db.Put("gps/mode", mymode)
         self.db.Put("gps/temp", temp/2.0)
         self.db.Get("gps/pos/here").SetPos(lat / 3600000.0, lon / 3600000.0)
         self.db.Get("gps/pos/here").alt_gps = gpsalt / 100.0
#         print "m12> here: ", self.db.Get("gps/pos/here")
        

      elif line[:2] == "Bb":   #sat vis message
         try:
            (vis,) = struct.unpack(">B", line[2])
         except :
            print "m12> error unpacking sat vis bytes"
            return

#         print "m12> vis %s" % str(vis)
         for i in range(3, 84, 7):
            try:
               (prn, doppler, el, az, health) = struct.unpack(">BhBHB", line[i:i+7])
            except:
               print "m12> error unpacking sat vis bytes"
               return
            if prn:
               self.prnEl[prn] = el
               self.prnAz[prn] = az
#               print "m12> prn %d dop %d az %d el %d h %d" % (prn, doppler, az, el, health)

         self.Seteas()
      
      elif line[:2] == "Cj":  #receiver id
         id = line[6:]
         print "m12> ", line[6:]


def Xsum(s):
   sum = 0
   for c in s: sum ^= ord(c)
   return sum
