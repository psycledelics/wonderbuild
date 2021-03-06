#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

try: from fnv import new as _Sig
except ImportError:
	try: from hashlib import md5 as _Sig
	except ImportError: from md5 import md5 as _Sig

class Sig(object):
	
	def __init__(self, *args):
		self._sig = _Sig()
		self.update(*args)

	def update(self, *args):
		for s in args:
			if s is not None: self._sig.update(s)
			self._sig.update('\0')
	
	def digest(self): return self._sig.digest()
