#!/usr/bin/python
#--------------------------------------------------------------------------
# Copyright 2003 William Orton - will@loopfree.net
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


#program to convert a EGM96 WGS84 geoid height 
#file to a more useful binary format
#http://164.214.2.59/GandG/wgsegm/egm96.html
#http://cddisa.gsfc.nasa.gov/926/egm96/egm96.html
#

#(for converting GPS altitude to MSL)

import struct

infile = "WW15MGH.GRD"
outfile = "geoid.bin"


ifile = open(infile, 'r')
ofile = open(outfile, 'wb')

paramline = ifile.readline()
paramline = paramline.strip()
params = [val for val in paramline.split(" ") if len(val) > 0]
print "params ", params

i = 0
points = 0

for line in ifile.xreadlines():
   line = line.rstrip()
   if len(line) < 1: continue
   vals = [val for val in line.split(" ") if len(val) > 0]

   for val in vals:
      binval = struct.pack("f", float(val))
      ofile.write(binval)
      points += 1


print "points processed: ", points
ofile.close()
ifile.close()