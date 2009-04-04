#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2007-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os

from logger import is_debug, debug
from signature import Sig
from option_cfg import OptionCfg

class FHSCfg(OptionCfg):
	'options for the Filesystem Hierarchy Standard'

	known_options = set([
		'dest-dir',
		'prefix-dir'
	])

	@staticmethod
	def generate_option_help(help):
		help['dest-dir']   = ('<dir>', 'use <dir> as staged install prefix', '<bld-dir>/staged-install')
		help['prefix-dir'] = ('<abs-dir>', 'use <abs-dir> as final install prefix', '/usr/local')

	def __init__(self, project):
		OptionCfg.__init__(self, project)
		
		try:
			old_sig, self.dest_path, self.prefix_path = \
				self.project.state_and_cache[self.__class__.__name__]
		except KeyError: parse = True
		else: parse = old_sig != self.options_sig
		
		if parse:
			if __debug__ and is_debug: debug('cfg: fhs: parsing options')
			
			o = self.options

			if 'dest-dir' in o: self.dest_path = o['dest-dir']
			else: self.dest_path = self.project.bld_node.abs_path
			
			if 'prefix-dir' in o: self.prefix_path = o['prefix-dir']
			else: self.prefix_path = os.path.join('usr', 'local')
			
			self.project.state_and_cache[self.__class__.__name__] = \
				self.options_sig, self.dest_path, self.prefix_path

