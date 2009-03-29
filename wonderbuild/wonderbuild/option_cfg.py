#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from signature import Sig

class OptionCfg(object):
	def __init__(self, project):
		self.project = project
		project.option_handler_classes.add(self.__class__)

	known_options = set()
	
	@staticmethod
	def help(help): pass
	
	@property
	def options(self): return self.project.options
	
	@property
	def options_sig(self):
		try: return self._options_sig
		except AttributeError:
			sig = Sig()
			options = self.options
			for name in self.__class__.known_options:
				value = options.get(name, None)
				if value is not None: sig.update(value)
			sig = self._options_sig = sig.digest()
			return sig
