#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from signature import Sig
from cmd import exec_subprocess

class Task(object):	
	def __init__(self, project, aliases = None):
		self.in_tasks = []
		self.out_tasks = []
		self.project = project
		project.add_aliases(self, aliases)
		project.tasks.append(self)

	def dyn_in_tasks(self): return None
		
	def process(self): pass
	
	def uid(self): return None
	
	def old_sig(self):
		try: return self.project.task_sigs[self.uid()]
		except KeyError: return None
	
	def actual_sig(self): return None
	
	def update_sig(self): self.project.task_sigs[self.uid()] = self.actual_sig()
	
class Obj(Task):
	def uid(self):
		try: return self._uid
		except AttributeError:
			sig = Sig(self.target.path).digest()
			self._uid = sig
			return sig

	def actual_sig(self):
		try: return self._actual_sig
		except AttributeError:
			sig = Sig(self.source.actual_sig).digest()
			self._actual_sig = sig
			return sig
		
	def process(self):
		if self.old_sig() != self.actual_sig():
			exec_subprocess(['c++', '-o', self.target.path, '-c', self.source.path])
			self.update_sig()
			return True
		else:
			self.out_tasks = []
			return False
		
class Lib(Task):
	def uid(self):
		try: return self._uid
		except AttributeError:
			sig = Sig(self.target.path).digest()
			self._uid = sig
			return sig

	def actual_sig(self):
		try: return self._actual_sig
		except AttributeError:
			sig = Sig()
			for s in self.sources: sig.update(s.actual_sig)
			sig = sig.digest()
			self._actual_sig = sig
			return sig

	def process(self):
		if self.old_sig() != self.actual_sig():
			exec_subprocess(['c++', '-o', self.target.path] + [s.path for s in self.sources])
			self.update_sig()
			return True
		else:
			self.out_tasks = []
			return False

