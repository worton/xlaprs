#!/usr/bin/python
#--------------------------------------------------------------------------
# Copyright 2003 William Orton - will@loopfree.net
#                Kevin Glueck  - kglueck@viz.tamu.edu
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. The license and distribution terms for any publically available version
#    or derivative of this code cannot be changed.  i.e. this code cannot 
#    simply be copied and put under another distribution license
#    [including, but not limited to, the GNU Public License.]
#
# THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL
# THE AUTHOR OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# --------------------------------------------------------------------------

import db, string, re, types, os, pickle, aprs

class Config:
   def __init__(self, db):
      self.db = db
      self.db.Put("global/config", self)
      self.dataprefix = "config/"
      self.metaprefix = "metaconfig/"
      self.filename = "xlaprs.conf"
      self.statename = "xlaprs.state"

   def Load(self):
      """Load entier config from persistent storage into DB"""

      f = file(self.filename, "r")
      items = []
      for line in f.xreadlines():
         if line[0] == '#':
            continue
         m = re.match(r'([^ ]) ([^ ]+) ([^ ]+) (.*)', line)
         (linetype, path, type, val) = m.group(1,2,3,4)
   
         if linetype == 'd':  #data line
            if type == "str":
               val = str(val)
            elif type == "int":
               val = int(val)
            self.db.Put(self.dataprefix + path, val)
         elif linetype == 'm':  #meta line
            if type == "str":
               val = str(val)
            self.db.Put(self.metaprefix + path, val)
   
      f.close()

#      self.db.Put("aprs/messages",{})
#      f = file(self.statename, "r")
#      messages = self.db.Get("aprs/messages")
#      for line in f.xreadlines():
#         if line[0] == '#':
#            continue
#         line = line.replace('\r','')
#         line = line.replace('\n','')
#         m = aprs.AprsMessage()
#         m.UnpackMessage(line)
#         messages[m.GetKey()] = m
#
#      f.close()

      try:
         filesize = os.stat(self.statename)[6]  # if filesize is > 0
      except OSError:
         # couldn't open file...setting filesize so load won't happen
         print "config> No state file found, defaulting values"
         filesize = 0

      if filesize:
         f = file(self.statename, "r")
         # nested try structs here.  the idea is that if stations data is
         # bad, then the messages is prolly also.  but what if stations is
         # good and messages is bad...that's why the two structs
         try:
            stations = pickle.load(f)
            print "config> unpickled stations"
            try:
               messages = pickle.load(f)
               print "config> unpickled messages"
            except:
               print "config> Bad message data found in %s, ignoring..." % self.statename
               messages = {}
         except:
            print "config> Bad station data found in %s, ignoring..." % self.statename
            stations = {}
            messages = {}
         f.close()
      else:
         stations = {}
         messages = {}
      self.db.Put("aprs/stations",stations)
      self.db.Put("aprs/messages",messages)

      
   def Save(self):
      """Save entire config to file from db"""
      f = file(self.filename, "w")
      all = self.db.GetAll()
      for (key, val) in all:
         if len(key) > 6 and key[0:6] == "config":
            k = key[7:]
            if isinstance(val, types.IntType):
               f.write("d %s int %d\n" % (k, val))
            elif isinstance(val, types.StringType):
               f.write("d %s str %s\n" % (k, val))
         elif len(key) > 10 and key[0:10] == "metaconfig":
            k = key[11:]
            if isinstance(val, types.IntType):
               f.write("m %s int %d\n" % (k, val))
            elif isinstance(val, types.StringType):
               f.write("m %s str %s\n" % (k, val))
      f.close()

      f = file(self.statename, "w")
      stations = self.db.Get("aprs/stations")
      messages = self.db.Get("aprs/messages")
      pickle.dump(stations,f)
      pickle.dump(messages,f)
      f.close()

      

if __name__ == "__main__":
   pass
