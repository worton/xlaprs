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

import struct

datfile = "/dev/shm/geoid.bin"

class Geoid:
   def __init__(self):
      self.dfile = open(datfile, 'rb')
      self.cols = 360 * 4 + 1  #0  -> 360 degrees of lon in .25deg increments
      self.rows = 180 * 4 + 1  #90 -> -90 degrees of lat in .25deg increments
      self.pointsize = 4       #32-bit floats

   def gps2msl(self, where, alt):
      return alt - self.Lookup(where)

   def msl2gps(self, where, alt):
      return alt + self.Lookup(where)

   def Lookup(self, where):
      (lat, lon) = where
      rowsdown = int((-lat + 90.0) * 4.0)
      if lon < 0: lon += 360.0
      colsover = int(lon * 4.0)
      index = rowsdown * self.cols + colsover

      self.dfile.seek(self.pointsize * index)
      f = self.dfile.read(self.pointsize)
      return struct.unpack("f", f)[0]

   def __getstate__(self):
      dict = {}
      dict['cols'] = self.cols
      dict['rows'] = self.rows
      dict['pointsize'] = self.pointsize
      return dict

   def __setstate__(self, data):
      self.cols = data['cols']
      self.rows = data['rows']
      self.pointsize = data['pointsize']
      self.dfile = open(datfile, 'rb')
