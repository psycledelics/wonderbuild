#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os, stat
try:
	from hashlib import md5
except ImportError:
	from md5 import md5

def hash_file(filename):
	'computes an md5 hash from a filename based its stat'
	st = os.stat(filename)
	if stat.S_ISDIR(st.st_mode): raise IOError, 'not a file'
	m = md5()
	m.update(str(st.st_mtime))
	#m.update(str(st.st_size))
	return m.digest() # or m.hexdigest()

if __name__ == '__main__':
	def four_bits_to_hexchar(b):
		b10 = b - 10
		if b10 >= 0: return chr(ord('a') + b10)
		return chr(ord('0') + b)
	def byte_to_hexstring(b):
		b = ord(b)
		return four_bits_to_hexchar(b >> 4) + four_bits_to_hexchar(b & 0xf)
	def raw_to_hexstring(s):
		r = ''
		for b in s: r += byte_to_hexstring(b)
		return r

	import sys
	for f in sys.argv[1:]: print raw_to_hexstring(hash_file(f)), f

