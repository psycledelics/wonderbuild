#! /usr/bin/env python

import os, stat, md5
def hash_file(filename):
	'computes an md5 hash from a filename based on modtime and size'
	st = os.stat(filename)
	if stat.S_ISDIR(st.st_mode): raise IOError, 'not a file'
	m = md5.md5()
	m.update(str(st.st_mtime))
	#m.update(str(st.st_size))
	return m.digest()

if __name__ == '__main__':
	def four_bits_to_hexchar(b):
		b10 = b - 10
		if b10 >= 0: return chr(ord('a') + b10)
		return chr(ord('0') + b)
	def byte_to_hexstring(b):
		b = ord(b)
		return four_bits_to_hexchar(b >> 4) + four_bits_to_hexchar(b & 0xf)
	def hex(s):
		r = ''
		for b in s: r += byte_to_hexstring(b)
		return r

	import sys
	f = sys.argv[0]
	print hex(hash_file(f)), f
