#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os, stat
try:
	from hashlib import md5
except ImportError:
	from md5 import md5

class Sig:
	def __init__(self, s = None):
		if s is None: self._impl = md5()
		else: self._impl = md5(s)
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

def four_bits_to_hexchar(b):
	b10 = b - 10
	if b10 >= 0: return chr(ord('a') + b10)
	return chr(ord('0') + b)
def byte_to_hexstring(b):
	b = ord(b)
	return four_bits_to_hexchar(b >> 4) + four_bits_to_hexchar(b & 0xf)
def raw_to_hexstring(s):
	# note python has an hex() builtin function but it does not accept a raw input string
	r = ''
	for b in s: r += byte_to_hexstring(b)
	return r

if __name__ == '__main__':
	# both lead to the same digest
	s = Sig('ab')
	print s.hexdigest()
	print raw_to_hexstring(s.digest())
	s = Sig()
	s.update('a')
	s.update('b')
	print s.hexdigest()
	print raw_to_hexstring(s.digest())
