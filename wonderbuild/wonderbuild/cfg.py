#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import threading

from logger import out, is_debug, debug, colored, silent
from options import options, known_options
from signature import Sig

class Cfg(object):
	def __init__(self, project):
		self.project = project
		project.cfgs.append(self)
		self.lock = threading.Lock()

	_options = set()
	
	def options(self):
		global known_options
		known_options |= self.__class__._options

	@property
	def options_sig(self):
		try: return self._options_sig
		except AttributeError:
			sig = Sig()
			for o in options:
				for oo in self.__class__._options:
					if o.startswith(oo + '='): sig.update(o)
			sig = self._options_sig = sig.digest()
			return sig

	def help(self): pass

	def configure(self): pass

	def print_desc(self, desc, color = '34'):
		if silent: return
		out.write(colored(color, 'wonderbuild: cfg: ' + desc + ':') + ' ')
		if __debug__ and is_debug: out.write('\n')
		out.flush()
		
	def print_result_desc(self, desc, color = '34'):
		if silent: return
		out.write(colored(color, desc))
		out.flush()
