#!/usr/bin/python

import types

class Db:
   latest = {}
   def Put(self, key, val):
      self.latest[key] = val

   def Get(self, key):
      try:
         val = self.latest[key]
      except KeyError:
         val = None
      return val

   def GetAll(self):
      keys = self.latest.keys()
      keys.sort()
      return [(key, self.latest[key]) for key in keys]
#      return self.latest.items().sort(lambda a, b: cmp(a[1], b[1]))


   def DumpLatest(self):
      print "db> dump of latest{}:"
      for (key, val) in self.GetAll():
         print "%-20s" % key,
         if isinstance(val, types.IntType):
            print "int   :%d" % val
         elif isinstance(val, types.FloatType):
            print "float :%f" % val
         elif isinstance(val, types.StringType):
            print "string:%s" % val
         elif isinstance(val, waypoint.Waypoint):
            print "waypoint:%s" % str(val)
         else:
            print "other :%s" % str(val)




#db keys
#gps/...                All GPS data
####gps/speed              float    current speed in knots
####gps/course             float    current course
#gps/dop                float    current dilution of precision
#gps/hdop               float    current horizontal DOP
#gps/vdop               float    current vertical DOP
#gps/mag                float    current magnetic compass deviation
#gps/mode               int      current GPS mode; 0=acquiring, 2=2D, 3=3D
#gps/temp               float    current GPS receiver temperature in C
#gps/pos/...
####gps/pos/alt            float    current altitude in meters
#gps/pos/here           waypoint current pos/alt in waypoint object
#gps/vector             vector   current course & speed in vector object
#gps/vvector            vector   current vertical vector (gps 3d spd - 2d speed)
####gps/pos/lat-deg        int      cunrret degrees of latitude; sign indicates hemisphere
####gps/pos/lat-min        float    current minutes of latitude; always positive
####gps/pos/lon-deg        int      cunrret degrees of longitude; sign indicates hemisphere
####gps/pos/lon-min        float    current minutes of longitude; always positive
#gps/pos/valid          int      current position valid? 1=yes 0=no
#gps/sat/...
#gps/sat/prn/eas:       dict     current sat status {prn: {'el': int, 'az': int, 'sig': int}, ...}
#gps/sat/prn/solution:  list     current list of prns in solution [int, ...]
#gps/sat/tracking:      int      current #of sats in solution
#gps/sat/visible:       int      current #of sats in sky
#gps/time/...
#gps/time/day: 10
#gps/time/hour: 6
#gps/time/minute: 6
#gps/time/month: 2
#gps/time/second: 53
#gps/time/valid: 1
#gps/time/year: 3
#
#aprs/...
#aprs/stations           dict     {"call-ssid" : AprsStation obj, ... } all station objects
#aprs/bytime             list     ["AD6XL-1", "KF6UZI-1", ...]
#aprs/bydistance         list     ["AD6XL-1", "KF6UZI-1", ...]
#aprs/byalpha            list     ["AD6XL-1", "KF6UZI-1", ...]
#aprs/byconfig           list     ["AD6XL-1", "KF6UZI-1", ...]  filtered/ordered list of callsigns by current config
#
#config/...              Persistent config
#config/display/
#config/aprs/sort        str  "time", "distance", "alpha"
#config/tnc/path         str  "WIDE2-2"
#config/tnc/unproto      str  "APZ242"
#config/misc/tz          int  timezone UTC offset
#
#global/...
#global/config           Config object
#global/router           Router object
#global/display          Display object
#global/screenlist       list of screen objects
#global/
