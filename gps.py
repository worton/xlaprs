#!/usr/bin/python

import db, waypoint, vector

class Gps:
   status = ""
   def __init__(self, db):
      self.db = db
      self.Initdbobjects()

   def Initdbobjects(self):
      """Set up any stat db objects we're going to be updating"""
      self.db.Put("gps/pos/here", waypoint.Waypoint())
      self.db.Put("gps/vector", vector.Vector())
      self.db.Put("gps/vvector", vector.VVector())
      self.db.Put("gps/sat/prn/eas", {})

      self.db.Put("gps/time/day", 0)
      self.db.Put("gps/time/month", 0)
      self.db.Put("gps/time/year", 0)
      self.db.Put("gps/time/hour", 0)
      self.db.Put("gps/time/minute", 0)
      self.db.Put("gps/time/second", 0)

      self.db.Put("gps/sat/tracking", 0)
      self.db.Put("gps/sat/visible", 0)

      self.db.Put("gps/dop", 0.0)
      self.db.Put("gps/temp", 0.0)


   def GetStatus(self):
      return self.status

   def Start(self):
      pass
   def Stop(self):
      pass
