#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os
from signature import Sig
from options import OptionDecl

class OptionCfg(OptionDecl):
	signed_options = set()
	signed_os_environ = set()

	def __init__(self, shared_holder):
		self.__shared_holder = shared_holder
		shared_holder.option_collector.option_decls.add(self.__class__)

	@property
	def options(self): return self.__shared_holder.options
	
	@property
	def options_sig(self):
		try: return self.__shared_holder.options_sigs[self.__class__]
		except AttributeError: self.__shared_holder.options_sigs = {}
		except KeyError: pass
		sig = Sig()
		options = self.__shared_holder.options
		for name in self.__class__.signed_options:
			value = options.get(name, None)
			if value is not None: sig.update(name + '=' + value)
		for name in self.__class__.signed_os_environ:
			value = os.environ.get(name, None)
			if value is not None: sig.update(name + '=' + value)
		sig = self.__shared_holder.options_sigs[self.__class__] = sig.digest()
		return sig
