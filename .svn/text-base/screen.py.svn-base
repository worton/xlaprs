#!/usr/bin/python

import threading, time, Queue

class Screen(threading.Thread):
   def __init__(self, db):
      threading.Thread.__init__(self)
      self.running = 0
      self.displaying = 0
      self.db = db
      self.lock = threading.Lock()
      self.disp = db.Get("global/display")
      self.status = "initted"
      self.commandq = Queue.Queue(5)

   def Start(self):
      if self.running: return
      self.running = 1
      self.lock.acquire()
      threading.Thread.start(self)
      self.status = "running"

   def Stop(self):
      if not self.running: return
      self.running = 0
      self.lock.release()
#      threading.Thread.join(self, 1)
      self.status = "stopped"

#router calls these
   def Show(self):
      self.displaying = 1
      self.init = 1
      self.lock.release()

   def Hide(self):
      self.lock.acquire()
      self.displaying = 0

   def EnqueueCommand(self, command):
      self.commandq.put(command, 1)

   def run(self):
      print "screen> running"

      while self.running:
         self.lock.acquire()
         if not self.running:   #we were just stopped!
            print "screen> exiting"
            return
         self.lock.release()

         while self.displaying:
            self.lock.acquire()
            while self.commandq.qsize():
               self.HandleCommand()
            if self.init:
               self.InitDraw()
               self.init = 0
            self.Draw()
            self.lock.release()
            time.sleep(.1)
      print "screen> exiting"


   def InitDraw(self, name=""):
      d = self.disp
      d.Clear()
      if name:
         d.SetPos((0,0))
         d.Write(name)
      d.Line((0,8), (119, 8))
      d.Line((119,0), (119, 8))

   def Draw(self):
      pass
   def HandleCommand(self):
      command = self.commandq.get(1)
      if command == "esc":
         self.db.Get("global/router").Relinquish()
