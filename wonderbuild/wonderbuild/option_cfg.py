#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from signature import Sig

from options import OptionDecl

class OptionCfg(OptionDecl):
	def __init__(self, project):
		self.project = project
		project.option_collector.option_decls.add(self.__class__)

	@property
	def options(self): return self.project.options
	
	@property
	def options_sig(self):
		try: return self._options_sig # TODO this could actually be stored in the project since it's per (project, class)
		except AttributeError:
			sig = Sig()
			options = self.options
			for name in self.__class__.known_options:
				value = options.get(name, None)
				if value is not None:
					if len(value) != 0: sig.update(value)
					else: sig.update('\0')
			sig = self._options_sig = sig.digest()
			return sig
