#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2009-2010 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from logger import silent, is_debug, debug, color_bg_fg_rgb
from task import Persistent, Task
from options import OptionDecl
from fhs import FHS
from signature import Sig

import os, errno, shutil
if os.name == 'posix':
	def install(src, dst):
		try: os.link(src, dst) # try to do a hard link
		except OSError, e:
			if e.errno != errno.EXDEV: raise 
			# error: cross-device link: dst is on another filesystem than src
			shutil.copy2(src, dst) # fallback to copying
else: # hard links unavailable, do a copy instead
	install = shutil.copy2

class InstallTask(Task, Persistent, OptionDecl):

	# OptionDecl
	known_options = set(['check-missing'])

	# OptionDecl
	@staticmethod
	def generate_option_help(help): help['check-missing'] = ('[yes|no]', 'check for missing built files (rebuilds files you manually deleted in the build dir)', 'yes')
	
	def __init__(self, project, name):
		Task.__init__(self)
		Persistent.__init__(self, project.persistent, name)
		self.name = name
		self.fhs = FHS.shared(project)
		self.check_missing = project.options.get('check-missing', 'yes') != 'no'

	def __str__(self): return \
		'install ' + self.name + ' from ' + str(self.trim_prefix) + \
		' to ' + str(self.dest_dir) # + ': ' + ' '.join([s.rel_path(self.trim_prefix) for s in self.sources])

	@property
	def trim_prefix(self): raise Exception, str(self.__class__) + ' did not redefine the property.'
	
	@property
	def sources(self): raise Exception, str(self.__class__) + ' did not redefine the property.'
	
	@property
	def dest_dir(self): raise Exception, str(self.__class__) + ' did not redefine the property.'

	# Task	
	def __call__(self, sched_ctx):
		if False: yield
		try: old_sig, sigs = self.persistent
		except KeyError:
			if __debug__ and is_debug: debug('task: no state: ' + str(self))
			old_sig = None
		sig = [s.sig for s in self.sources]
		sig.sort()
		sig = Sig(''.join(sig))
		sig.update(self.dest_dir.abs_path)
		sig = sig.digest()
		if old_sig == sig and not self.check_missing:
				if __debug__ and is_debug: debug('task: skip: no change: ' + str(self))
		else:
			need_process = False
			if old_sig is None:
				sigs = {}
				changed_sources = self.sources
				removed_sources = []
				need_process = True
			else:
				changed_sources = []
				for s in self.sources:
					try: source_sig = sigs[s]
					except KeyError:
						# This is a new source.
						if __debug__ and is_debug: debug('task: no state: ' + str(s))
						changed_sources.append(s)
					else:
						if source_sig != s.sig:
							# The source changed.
							if __debug__ and is_debug: debug('task: sig changed: ' + str(s))
							changed_sources.append(s)
						elif self.check_missing:
							rel_path = s.rel_path(self.trim_prefix)
							dest = self.dest_dir / rel_path
							if not dest.exists:
								if __debug__ and is_debug: debug('task: target missing: ' + str(dest))
								changed_sources.append(s)
				if len(changed_sources) != 0: need_process = True
				# deinstall removed sources
				removed_sources = []
				for s in sigs:
					if not s in self.sources: removed_sources.append(s)
				if len(removed_sources) != 0:
					# Some sources have been removed from the list of sources.
					need_process = True
				elif not need_process and old_sig != sig:
					# it's self.dest_dir that changed (non exclusive, actually).
					# to be complete, we should remove the files in the old destination,
					# but only if that old destination overlaps with the new one.
					changed_sources = self.sources
					need_process = True
			if not need_process:
				if __debug__ and is_debug: debug('task: skip: no change: ' + str(self))
			else:
				for s in changed_sources: sigs[s] = s.sig
				sched_ctx.lock.release()
				try:
					self.dest_dir.lock.acquire()
					try:
						install_tuples = []
						for s in changed_sources:
							rel_path = s.rel_path(self.trim_prefix)
							dest = self.dest_dir / rel_path
							install_tuples.append((s, dest, False, rel_path))
						for s in removed_sources:
							rel_path = s.rel_path(self.trim_prefix)
							dest = self.dest_dir / rel_path
							install_tuples.append((s, dest, True, rel_path))
						if not silent and len(install_tuples) != 0:
							list = [(t[2] and '-' or '+') + t[3] for t in install_tuples]
							list.sort()
							self.print_desc_multi_column_format(
								str(self.dest_dir)+ ': installing ' + self.name + ' from ' + str(self.trim_prefix),
								list, color_bg_fg_rgb((220, 220, 220), (70, 100, 150))
							)
						for t in install_tuples:
							s, dest, deinstall = t[0], t[1], t[2],# t[3]
							if deinstall:
								if dest.exists: os.remove(dest.path)
								del sigs[s]
							else:
								if dest.exists: os.remove(dest.path)
								else: dest.parent.make_dir()
								install(s.path, dest.path)
							dest.clear()
						self.persistent = sig, sigs
					finally: self.dest_dir.lock.release()
				finally: sched_ctx.lock.acquire()
