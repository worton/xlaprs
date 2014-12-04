#!/usr/bin/python

import screen, widget, config

class ConfigScreen(screen.Screen):
   def __init__(self, db):
      screen.Screen.__init__(self, db)
      self.id = id

      self.page = 0
      self.editing = 0
      self.sel = 0
      self.dirty = 0
      self.pos = [(0,10),(0,18),(0,26),(0,34),(0,42),(0,50)]
      self.wlines = [widget.ConfigLine((6,10), self.disp, self.db),
                     widget.ConfigLine((6,18), self.disp, self.db),
                     widget.ConfigLine((6,26), self.disp, self.db),
                     widget.ConfigLine((6,34), self.disp, self.db),
                     widget.ConfigLine((6,42), self.disp, self.db),
                     widget.ConfigLine((6,50), self.disp, self.db)]
      self.numlines = len(self.wlines)

      self.ckeys = []
      wholedb = self.db.GetAll()
      wholedb.sort()
      for (key, val) in wholedb:
         if len(key) > 6 and key[0:6] == "config":
            self.ckeys.append(key)


   def InitLines(self):
      i = self.page * self.numlines
      for w in self.wlines:
         if i < len(self.ckeys):
            w.SetKey(self.ckeys[i])
         else:
            w.SetKey("")
         i += 1

   def InitDraw(self):
      screen.Screen.InitDraw(self, "Config")
      self.DrawCursor(0)
      self.InitLines()
      for w in self.wlines:
         w.InitDraw()

   def Draw(self):
      if self.dirty:
         self.wlines[self.sel].Draw()
         self.dirty = 0

   def DrawCursor(self, newsel):
      if self.sel != newsel: #we moved (vs. only  edit/unedit), so need to erase
         self.disp.SetPos(self.pos[self.sel])
         self.disp.Write(" ")
         self.sel = newsel
      self.disp.SetPos(self.pos[self.sel])
      if self.editing:
         self.disp.Write("*")
      else:
         self.disp.Write(">")

            

   def HandleCommand(self):
      command = self.commandq.get(1)
      if command == "esc":
         if self.editing:
            self.dirty = 1
            self.wlines[self.sel].Esc()
            self.editing = 0
            self.DrawCursor(self.sel)
         else:
            self.db.Get("global/router").Relinquish()

      elif command == "enter":
         self.dirty = 1
         if self.editing:
            self.wlines[self.sel].Save()
            self.editing = 0
            self.DrawCursor(self.sel)
         else:
            self.editing = 1
            self.DrawCursor(self.sel)
            self.wlines[self.sel].Edit()
         
      elif command == "left":
         if self.editing:
            self.dirty = 1
            self.wlines[self.sel].Left()
         else:
            config = self.db.Get("global/config")
            config.Save()

      elif command == "right":
         if self.editing:
            self.dirty = 1
            self.wlines[self.sel].Right()

      elif command == "up":
         if self.editing:
            self.dirty = 1
            self.wlines[self.sel].Up()
         else:
            newsel = self.sel - 1
            if newsel < 0:
               self.page -= 1
               if self.page < 0:
                  self.page = 0
                  newsel = 0
               else:
                  newsel = self.numlines - 1
               self.InitLines()
            self.DrawCursor(newsel)

      elif command == "down":
         if self.editing:
            self.dirty = 1
            self.wlines[self.sel].Down()
         else:
            newsel = self.sel + 1
            if newsel == self.numlines:
               newsel = 0
               self.page += 1
               self.InitLines()
            self.DrawCursor(newsel)

