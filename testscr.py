#!/usr/bin/python

import time, screen

class TestScreen(screen.Screen):
   def __init__(self, db, id):
      screen.Screen.__init__(self, db)
      self.id = id
      

   def InitDraw(self):
      screen.Screen.InitDraw(self)
      self.disp.Write("test display %s" % self.id)
   def Draw(self):
      self.disp.Write("-")
   def HandleCommand(self, command):
      screen.Screen.HandleCommand(self, command)
      print "TestScreen> command %s" % command
      if command == "esc":
         self.db.Get("global/router").Relinquish()
