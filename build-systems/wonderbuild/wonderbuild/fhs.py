#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2007-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os

from logger import is_debug, debug
from signature import Sig
from option_cfg import OptionCfg
from task import Persistent

class FHS(OptionCfg, Persistent):
	'options for the Filesystem Hierarchy Standard'
	
	signed_os_environ = set(['DESTDIR', 'PREFIX'])

	signed_options = set([
		'install-dest-dir',
		'install-prefix-dir'
	])
	
	known_options = signed_options

	@staticmethod
	def generate_option_help(help):
		help['install-dest-dir']   = ('<dir>', 'use <dir> as staged install prefix', 'DESTDIR env var: ' + os.environ.get('DESTDIR', '(not set, defaults to <bld-dir>/staged-install)'))
		help['install-prefix-dir'] = ('<abs-dir>', 'use <abs-dir> as final install prefix', 'PREFIX env var: ' + os.environ.get('PREFIX', '(not set, defaults to /usr/local)'))

	@staticmethod
	def shared(project):
		try: return project.__fhs
		except AttributeError:
			instance = project.__fhs = FHS(project)
			return instance

	def __init__(self, project):
		OptionCfg.__init__(self, project)
		Persistent.__init__(self, project.persistent, str(self.__class__))
		
		try:
			old_sig, self.dest, prefix_path = self.persistent
		except KeyError: parse = True
		else: parse = old_sig != self.options_sig
		if parse:
			if __debug__ and is_debug: debug('cfg: fhs: parsing options')
			o = self.options

			dest = o.get('install-dest-dir', None) or os.environ.get('DESTDIR', None)
			if dest is not None: self.dest = project.fs.cur / dest
			else: self.dest = project.bld_dir / 'staged-install'
			
			prefix_path = o.get('install-prefix-dir', None) or os.environ.get('PREFIX', None) or os.path.join(os.sep, 'usr', 'local')
			if prefix_path.startswith(os.sep): prefix_path = prefix_path[len(os.sep):]
			else: raise Exception, 'invalid install-prefix-dir option: prefix must be an absolute path. got: ' + prefix_path
			
			self.persistent = self.options_sig, self.dest, prefix_path

		self.prefix = self.dest / prefix_path
		self.exec_prefix = self.prefix
		self.bin = self.exec_prefix / 'bin'
		self.lib = self.exec_prefix / 'lib'
		self.libexec = self.exec_prefix / 'libexec'
		self.include = self.prefix / 'include'
		self.share = self.prefix / 'share'
