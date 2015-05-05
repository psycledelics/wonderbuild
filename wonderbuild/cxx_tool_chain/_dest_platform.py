#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2007-2013 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from wonderbuild.signature import Sig
from wonderbuild.logger import is_debug, debug

class DestPlatform(object):
	def __init__(self):
		self.bin_fmt = None
		self.os = None
		self.arch = None
		self.pic_flag_defines_pic = None

	def clone(self, class_ = None):
		if class_ is None: class_ = self.__class__
		if __debug__ and is_debug: debug('cfg: dest platform: clone: ' + str(class_))
		c = class_()
		c.bin_fmt = self.bin_fmt
		c.os = self.os
		c.arch = self.arch
		c.pic_flag_defines_pic = self.pic_flag_defines_pic
		return c

	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			sig = Sig(self.bin_fmt, self.os, self.arch)
			if self.pic_flag_defines_pic is not None: sig.update(str(self.pic_flag_defines_pic))
			sig = self._sig = sig.digest()
			return sig
