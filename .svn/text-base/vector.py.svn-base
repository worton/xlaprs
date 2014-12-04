#!/usr/bin/python

import time, string, units


class Vector(object):
   def __init__(self):
      self.myspeed = 0.0            #m/sec
      self.mycourse = 0.0           #true course

      self.lastupdatetime = 0.0   #last time anything was updated
      self.lastmovedtime = 0.0    #last time speed went above lowspeedthresh
      self.lowspeedthresh = units.mi2km(0.9) / 3.6  #0.9mph threshold

   #
   # speed property
   #
   def GetSpeed_ms(self): return self.GetSpeed(lambda s: s)
   def SetSpeed_ms(self, spd): self.SetSpeed(spd, lambda s: s)
   def GetSpeed_kn(self): return self.GetSpeed(lambda s: units.km2nm(s * 3.6))
   def SetSpeed_kn(self, spd): self.SetSpeed(spd, lambda s: units.nm2km(spd) / 3.6)
   def GetSpeed_mph(self): return self.GetSpeed(lambda s: units.km2mi(s * 3.6))
   def SetSpeed_mph(self, spd): self.SetSpeed(spd, lambda s: units.mi2km(s) / 3.6)

   speed_ms = property(GetSpeed_ms, SetSpeed_ms)      #meters/sec
   speed_kn = property(GetSpeed_kn, SetSpeed_kn)      #knots
   speed_mph = property(GetSpeed_mph, SetSpeed_mph)   #miles/hour

   def GetSpeed(self, conv):
      return conv(self.myspeed)

   def SetSpeed(self, spd, conv):
      self.myspeed = conv(spd)
      if self.myspeed > self.lowspeedthresh:
         self.lastmovedtime = time.time()

   def IsMoving(self):
      return self.speed_mph >= self.lowspeedthresh

   #
   # course property
   #
   def SetCourse(self, course):
      if not self.LowSpeed():
         self.mycourse = course
   def GetCourse(self):
      return self.mycourse
   course = property(GetCourse, SetCourse)


   def LowSpeed(self):
      if self.myspeed < self.lowspeedthresh:
         return 1
      else:
         return 0

   def __str__(self):
      return "%05.2f mph course %5.1f" % (self.speed_mph, self.course)


class VVector(object):

   #samples are of altitude in centimeters

   def __init__(self):
      self.samples = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
      self.fpm = 0

   def PutSample(self, val):
      del self.samples[0]
      self.samples.append(int(val))
      self.CalcFPM()

   def CalcFPM(self):
      delta = 0
      lastsample = self.samples[0]
      for s in self.samples[1:-1]:
         delta += s - lastsample
         lastsample = s
      self.fpm = units.m2f(delta/100.0) * 60 / len(self.samples)



if __name__ == "__main__":
   pass
