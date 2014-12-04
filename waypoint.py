#!/usr/bin/python

import time, string, units, types, math, geoid


class Waypoint(object):
   def __init__(self):
      self.name = ""
      self.latdeg = 0
      self.latmin = 0.0
      self.londeg = 0
      self.lonmin = 0.0
      self.myalt = 0.0       #alt MSL, includes geoidal separation correction

      self.g = geoid.Geoid()

#alt properties
   def GetAlt_m(self): return self.myalt
   def SetAlt_m(self, alt): self.myalt = alt
   alt_m = property(GetAlt_m, SetAlt_m)

   def GetAlt_f(self): return units.m2f(self.myalt)
   def SetAlt_f(self, alt): self.myalt = units.f2m(alt)
   alt_f = property(GetAlt_f, SetAlt_f)

   #GPS alt has to apply/remove geoid correction
   def GetAlt_gps(self): return self.g.msl2gps(self.GetDeg(), self.myalt)
   def SetAlt_gps(self, alt): self.myalt = self.g.gps2msl(self.GetDeg(), alt)
   alt_gps = property(GetAlt_gps, SetAlt_gps)

   def SetPos(self, lat, lon):
      """Set self from lat, lon, each of which can be:
         35.2       -> 35.2 degrees north
         (35, 12.3) -> 35 degrees, 12.3 minutes north
         '3512.34N' -> 35 degrees, 12.34 minutes north (APRS format DDMM.MMH)

         -120.1       -> 120.1 degrees west
         (-120, 6.52)  -> 120 degrees, 6.52 minutes west
         '12006.52W'  -> 120 degrees, 6.52 minutes west (APRS format DDDMM.MMH)
         """

      if isinstance(lat, types.FloatType) and isinstance(lon, types.FloatType):
         #set from fractional degrees
         (self.latmin, self.latdeg) = math.modf(lat)
         self.latmin = abs(self.latmin * 60.0)

         (self.lonmin, self.londeg) = math.modf(lon)
         self.lonmin = abs(self.lonmin * 60.0)

      elif isinstance(lat, types.TupleType) and isinstance(lon, types.TupleType):
         (self.latdeg, self.latmin) = lat
         (self.londeg, self.lonmin) = lon

      elif isinstance(lat, types.StringType) and isinstance(lon, types.StringType):
         if len(lat) != 8 or len(lon) != 9:
            print "Waypoint> tried to set with bad strings lat %s lon %s" % (lat, lon)
            return
#WDOFIX check for valid conversions here
         try:
            self.latdeg = int(lat[0:2])
            self.latmin = float(lat[2:7])
            if lat[7] == "S": self.latdeg = -self.latdeg

            self.londeg = int(lon[0:3])
            self.lonmin = float(lon[3:8])
            if lon[8] == "W": self.londeg = -self.londeg
         except:
            pass

      else:
         print "Waypoint> unknown type in SetPos"

   def BearingTo(self, to):
      if self.latdeg == to.latdeg and self.londeg == to.londeg and self.latmin == to.latmin and self.lonmin == to.lonmin:
         print "waypoint> bearing to self, returning 0"
         return 0.0

      if self.latdeg >= 0:
         lat1 = deg2rad((float(self.latdeg)) + (self.latmin / 60.0))
      else:
         lat1 = deg2rad((float(self.latdeg)) - (self.latmin / 60.0))

      if self.londeg >= 0:
         lon1 = deg2rad(-((float(self.londeg)) + (self.lonmin / 60.0)))
      else:
         lon1 = deg2rad(-((float(self.londeg)) - (self.lonmin / 60.0)))

      if to.latdeg >= 0:
         lat2 = deg2rad((float(to.latdeg)) + (to.latmin / 60.0))
      else:
         lat2 = deg2rad((float(to.latdeg)) - (to.latmin / 60.0))

      if to.londeg >= 0:
         lon2 = deg2rad(-((float(to.londeg)) + (to.lonmin / 60.0)))
      else:
         lon2 = deg2rad(-((float(to.londeg)) - (to.lonmin / 60.0)))

      d = self.GCArc(to)
      if math.sin(lon2 - lon1) <= 0.0:
         c = acos_safe((math.sin(lat2) - math.sin(lat1) * math.cos(d)) / (math.sin(d) * math.cos(lat1)))
      else:
         c = 2 * math.pi - acos_safe((math.sin(lat2) - math.sin(lat1) * math.cos(d)) / (math.sin(d) * math.cos(lat1)))
      return rad2deg(c)


   def DistanceTo(self, to):
      return units.nm2mi(self.GCArc(to) * 180.0 * 60.0 / math.pi)

   def GCArc(self, to):
      if self.latdeg >= 0:
         lat1 = deg2rad((float(self.latdeg)) + (self.latmin / 60.0))
      else:
         lat1 = deg2rad((float(self.latdeg)) - (self.latmin / 60.0))

      if self.londeg >= 0:
         lon1 = deg2rad(-((float(self.londeg)) + (self.lonmin / 60.0)))
      else:
         lon1 = deg2rad(-((float(self.londeg)) - (self.lonmin / 60.0)))


      if to.latdeg >= 0:
         lat2 = deg2rad((float(to.latdeg)) + (to.latmin / 60.0))
      else:
         lat2 = deg2rad((float(to.latdeg)) - (to.latmin / 60.0))

      if to.londeg >= 0:
         lon2 = deg2rad(-((float(to.londeg)) + (to.lonmin / 60.0)))
      else:
         lon2 = deg2rad(-((float(to.londeg)) - (to.lonmin / 60.0)))

      d = 2.0 * asin_safe(math.sqrt(math.pow(math.sin((lat1-lat2)/2.0), 2) + 
                     math.cos(lat1) * math.cos(lat2) * math.pow(math.sin((lon1-lon2)/2.0), 2)))
      return d



   def Valid(self):
      return self.latdeg and self.latmin and self.londeg and self.lonmin

   def GetLat(self):
      """Return str of lat in DD MM.XXXN format"""
      return "%3d %06.3f%s" % (abs(self.latdeg), self.latmin, self.GetLatChar())
         
   def GetLon(self):
      """Return str of lon in DDD MM.XXXW format"""
      return "%3d %06.3f%s" % (abs(self.londeg), self.lonmin, self.GetLonChar())

   def GetLatAPRS(self):
      """Return str of lat in DDMM.XXN format"""
      return "%02.0f%05.2f%s" % (abs(self.latdeg), self.latmin, self.GetLatChar())

   def GetLonAPRS(self):
      """Return str of lon in DDDMM.XXW format"""
      return "%03.0f%05.2f%s" % (abs(self.londeg), self.lonmin, self.GetLonChar())

   def __str__(self):
      return self.GetLat() + " " + self.GetLon() + " %3.1fft" % self.GetAlt_f()

   def GetLatChar(self):
      if self.latdeg >= 0:
         return "N"
      else:
         return "S"

   def GetLonChar(self):
      if self.londeg >= 0:
         return "E"
      else:
         return "W"

   def GetDeg(self):
      """Return tuple of (lat, lon) in fractional degrees"""
      if self.latdeg < 0:
         lat = -(abs(self.latdeg) + self.latmin / 60.0)
      else:
         lat =       self.latdeg  + self.latmin / 60.0

      if self.londeg < 0:
         lon = -(abs(self.londeg) + self.lonmin / 60.0)
      else:
         lon =       self.londeg  + self.lonmin / 60.0
         
      return (lat, lon)


def deg2rad(deg):
   return deg * math.pi / 180.0

def rad2deg(rad):
   return rad * 180.0 / math.pi

def asin_safe(x):
   return math.asin(max(-1.0, min(x, 1.0)))

def acos_safe(x):
   return math.acos(max(-1.0, min(x, 1.0)))


if __name__ == "__main__":
   a = Waypoint() 
   b = Waypoint() 
   a.SetPos((35, 1.0), (-120, 1.1))
   b.SetPos((34, 1.0), (-120, 1.1))  
   print a.BearingTo(b)   
   print b.BearingTo(a)
