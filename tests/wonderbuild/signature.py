#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os, stat
try:
	from hashlib import md5
except ImportError:
	from md5 import md5

class Sig:
	def __init__(self): self._impl = md5()
	def update(self, s): self._impl.update(s)
	def digest(self): return self._impl.digest()
	def hexdigest(self): return self._impl.hexdigest()

class Signed:
	def sig(self):
		try: return self._sig
		except AttributeError:
			self._sig = Sig()
			self.update_sig(self._sig)
			return self._sig

	def update_sig(self, sig): pass

def stat_sig(sig, st):
	'computes an md5 hash from a file stat'
	if stat.S_ISDIR(st.st_mode): raise IOError, 'not a file'
	sig.update(str(st.st_mtime))
	#sig.update(str(st.st_size))

def file_sig(sig, file_name):
	'computes an md5 hash from a filename based on its stat'
	st = os.stat(file_name)
	stat_sig(sig, st)

if __name__ == '__main__':
	def four_bits_to_hexchar(b):
		b10 = b - 10
		if b10 >= 0: return chr(ord('a') + b10)
		return chr(ord('0') + b)
	def byte_to_hexstring(b):
		b = ord(b)
		return four_bits_to_hexchar(b >> 4) + four_bits_to_hexchar(b & 0xf)
	def raw_to_hexstring(s):
		# note python has an hex() builtin function ...
		r = ''
		for b in s: r += byte_to_hexstring(b)
		return r

	import sys
	sig = Sig()
	for f in sys.argv[1:]:
		sig1 = Sig()
		file_sig(sig1, f)
		digest = sig1.digest()
		print raw_to_hexstring(digest), f
		sig.update(digest)
	print 'all:', raw_to_hexstring(sig.digest())

	if False: # both lead to the same digest
		s = Sig()
		s.update('a')
		s.update('b')
		print raw_to_hexstring(s.digest())
	
		s = Sig()
		s.update('ab')
		print raw_to_hexstring(s.digest())

