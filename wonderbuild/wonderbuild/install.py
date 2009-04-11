#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2009-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from logger import silent, is_debug, debug
from task import Task
from option_cfg import OptionCfg
from signature import Sig

import sys, os, shutil
if sys.platform.startswith('win'):
	def install(src, dst): shutil.copy2(src, dst)
else:
	def install(src, dst):
		try: os.link(src, dst)
		except OSError: shutil.copy2(src, dst)

class InstallTask(Task, OptionCfg):
	known_options = set(['check-missing'])

	@staticmethod
	def generate_option_help(help): help['check-missing'] = ('<yes|no>', 'check for missing built files (rebuilds files you manually deleted in the build dir)', 'no')
	
	def __init__(self, project):
		Task.__init__(self, project)
		OptionCfg.__init__(self, project)

		try: old_sig, self.check_missing = self.project.state_and_cache[self.__class__.__name__]
		except KeyError: parse = True
		else: parse = old_sig != self.options_sig
		if parse:
			if __debug__ and is_debug: debug('cfg: install: user: parsing options')
			o = self.options

			if 'check-missing' in o: self.check_missing = o['check-missing'] == 'yes'
			else: self.check_missing = False

			self.project.state_and_cache[self.__class__.__name__] = self.options_sig, self.check_missing

	@property
	def uid(self):
		try: return self._uid
		except AttributeError:
			self._uid = self.__class__.__name__ + '#' + str(self.sources[0])
			return self._uid
	
	@property
	def trim_prefix(self): raise Exception, str(self.__class__) + ' did not redefine the property.'
	
	@property
	def sources(self): raise Exception, str(self.__class__) + ' did not redefine the property.'
	
	@property
	def dest_dir(self): raise Exception, str(self.__class__) + ' did not redefine the property.'
	
	def __call__(self, sched_ctx):
		try: old_sig = self.project.state_and_cache[self.uid]
		except KeyError: old_sig = None
		sigs = [s.sig for s in self.sources]
		sigs.sort()
		sig = Sig(''.join(sigs))
		sig.update(self.dest_dir.abs_path)
		sig = sig.digest()
		need_process = old_sig != sig
		if not need_process and self.check_missing:
				for s in self.sources:
					dest = self.dest_dir / s.rel_path(self.trim_prefix)
					if not dest.exists:
						if __debug__ and is_debug: debug('task: destination missing: ' + str(dest))
						need_process = True
						break
		if need_process:
			sched_ctx.lock.release()
			try:
				self.dest_dir.lock.acquire()
				try:
					if not silent: self.print_desc(
						'installing from ' + str(self.trim_prefix) +
						' to ' + str(self.dest_dir) +
						':\n\t' + '\n\t'.join([s.rel_path(self.trim_prefix) for s in self.sources]),
						'47;34'
					)
					for s in self.sources:
						dest = self.dest_dir / s.rel_path(self.trim_prefix)
						if dest.exists: os.remove(dest.path)
						else: dest.parent.make_dir()
						install(s.path, dest.path)
					self.project.state_and_cache[self.uid] = sig
				finally: self.dest_dir.lock.release()
			finally: sched_ctx.lock.acquire()
