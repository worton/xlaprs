#!/usr/bin/python

import time, screen, waypoint, vector, widget, units, aprs, copy, math

def deg2rad(deg): return (deg - 90.0) * math.pi / 180.0

class MapScreen(screen.Screen):
   def __init__(self, db):
      screen.Screen.__init__(self, db)
      self.id = id
      self.db = db
      self.scale = 5.0   #miles/pixel
      self.center = (120,32)
      
   def InitDraw(self):
      pass
#      screen.Screen.InitDraw(self, "APRS Map")

   def Draw(self):
      showme = self.db.Get("config/aprs/showme")

      self.disp.SetFont(5)

      calls = self.db.Get("aprs/bydistance")
      here = self.db.Get("gps/pos/here")

      # do distance filtering
      filteredcalls = []
      locs = {}
      filterdist = 120*self.scale
      for call in calls:
         if here.DistanceTo(self.db.Get("aprs/stations")[call].where) <= filterdist:
            filteredcalls.append(call)
            locs[call] = self.db.Get("aprs/stations")[call].where
      calls = copy.copy(filteredcalls)




      self.disp.Clear()

#      if showme:
#         self.disp.SetPos(self.center)
      self.disp.Pixel(self.center)

      for call in calls:
         pos = [0,0]
         d = here.DistanceTo(locs[call])
         b = here.BearingTo(locs[call])
         pos[0] = self.center[0] + d / self.scale * math.cos(deg2rad(b))
         pos[1] = self.center[1] + d / self.scale * math.sin(deg2rad(b))

         if pos[0] > 0 and pos[0] < 240 and pos[1] > 0 and pos[1] < 64:
            self.disp.SetPos(pos)
            self.disp.Pixel(pos)
            pos = (pos[0]+2, pos[1]-2)
            if pos[0] > 0 and pos[0] < 240 and pos[1] > 0 and pos[1] < 64:
               self.disp.SetPos(pos)
               self.disp.Write(call)

      self.disp.SetFont(1)
      time.sleep(2)

   def HandleCommand(self):
      command = self.commandq.get(1)
      if command == "esc":
         self.db.Get("global/router").Relinquish()
      elif command == "left":
         pass
      elif command == "right":
         pass
      elif command == "down":
         self.scale = max(self.scale - 0.5, 0.0)
      elif command == "up":
         self.scale += 0.5


