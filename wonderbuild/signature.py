#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

try: from hashlib import md5 as Sig
except ImportError: from md5 import md5 as Sig

def raw_to_hexstring(s):
	# note same as 'foo'.encode('hex')
	if s is None: return None
	def byte_to_hexstring(b):
		def four_bits_to_hexchar(b):
			b10 = b - 10
			if b10 >= 0: return chr(ord('a') + b10)
			return chr(ord('0') + b)
		b = ord(b)
		return four_bits_to_hexchar(b >> 4) + four_bits_to_hexchar(b & 0xf)
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
