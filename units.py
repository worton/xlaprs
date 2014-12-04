#!/usr/bin/python

#meters & feet
def m2f(m):  return m * 3.28083989501
def f2m(ft): return ft * 0.3048
#yard = 0.9144meters, exactly, by definition. ft = 1/3 yard
      
#miles and kilometers
def mi2km(mi): return mi * 1.609344
def km2mi(km): return km * .621371192237
      
#nautical miles and miles
def mi2nm(mi): return mi * 0.8689752
def nm2mi(nm): return nm * 1.0 / 0.8689752

#nautical miles and kilometers
def km2nm(km): return mi2nm(km2mi(km))
def nm2km(nm): return mi2km(nm2mi(nm))
      

#compass stuff
def HeadingDiff(a, b):
   return min(abs(a-b), abs(a-b-360.0))

def CompassOrd2(c):
   """8-point ordinal"""
   while c > 360: c-= 360
   if c < 0: return "?!"
   elif c > 0 and c < 22.5: return " N"
   elif c >= 22.5 and c < 67.5: return "NE"
   elif c >= 67.5 and c < 112.5: return " E"
   elif c >= 112.5 and c < 157.5: return "SE"
   elif c >= 157.5 and c < 202.5: return " S"
   elif c >= 202.5 and c < 247.5: return "SW"
   elif c >= 247.5 and c < 292.5: return " W"
   elif c >= 292.5 and c < 337.5: return "NW"
   elif c >= 337.5 and c <= 360: return " N"
   elif c == 0: return "??"

def CompassOrd3(c):
   """16-point ordinal"""
   while c > 360: c-= 360

   if c < 0: return "?!"
   elif c > 0 and c < 11.25: return " N "
   elif c >= 11.25 and c < 33.75: return "NNE"
   elif c >= 33.75 and c < 56.25: return " NE"
   elif c >= 56.25 and c < 78.75: return "ENE"
   elif c >= 78.75 and c < 101.25: return " E "

   elif c >= 101.25 and c < 123.75: return "ESE"
   elif c >= 123.75 and c < 146.25: return " SE"
   elif c >= 146.25 and c < 168.75: return "SSE"
   elif c >= 168.75 and c < 191.25: return " S "

   elif c >= 191.25 and c < 213.75: return "SSW"
   elif c >= 213.75 and c < 236.25: return " SW"
   elif c >= 236.25 and c < 258.75: return "WSW"
   elif c >= 258.75 and c < 281.25: return " W "

   elif c >= 281.25 and c < 303.75: return "WNW"
   elif c >= 303.75 and c < 326.25: return " NW"
   elif c >= 326.25 and c < 348.75: return "NNW"
   elif c >= 348.75 and c <= 360: return " N "

   elif c == 0: return "???"
