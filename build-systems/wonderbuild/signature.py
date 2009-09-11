#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

try: from hashlib import md5 as _Sig
except ImportError: from md5 import md5 as _Sig

class Sig(object):
	def __init__(self, s): self._sig = Sig(s + '\0')
	def update(self, s): self._sig.update(s + '\0')
	def digest(self): return self._sig.digest()
