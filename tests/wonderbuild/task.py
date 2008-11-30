#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import sys, os, subprocess

from signature import Sig, raw_to_hexstring
from logger import is_debug, debug

class Task(object):	
	def __init__(self, project, aliases = None):
		self.in_tasks = []
		self.out_tasks = []
		#self.in_nodes = []
		#self.out_nodes = []
		self.processed = False
		self.executed = False
		self.project = project
		project.add_aliases(self, aliases)
		project.tasks.append(self)

	def add_in_task(self, task):
		self.in_tasks.append(task)
		task.out_tasks.append(self)

	def add_out_task(self, task):
		self.out_tasks.append(task)
		task.in_tasks.append(self)

	def dyn_in_tasks(self): return None
		
	def process(self): pass
	
	def uid(self): return None
	
	def old_sig(self):
		try: return self.project.task_sigs[self.uid()]
		except KeyError: return None
	
	def actual_sig(self): return None
	
	def update_sig(self): self.project.task_sigs[self.uid()] = self.actual_sig()
	
class Obj(Task):
	def __init__(self, project):
		Task.__init__(self, project)
		self.paths = []
		self.defines = {}
		self.flags = []
		
	def uid(self):
		try: return self._uid
		except AttributeError:
			sig = self._uid = Sig(self.target.path).digest()
			return sig

	def actual_sig(self):
		try: return self._actual_sig
		except AttributeError:
			sig = self._actual_sig = self.source.sig_to_string()
			return sig
		
	def process(self):
		self.target.parent.make_dir()
		I = []
		for p in self.paths: I += ['-I', p.path]
		D = []
		for k, v in self.defines.iteritems():
			if v is None: D.append('-D' + k)
			else: D.append('-D' + k + '=' + v)
		return exec_subprocess(['c++', '-o', self.target.path, '-c', self.source.path] + I + D + self.flags)
		
class Lib(Task):
	def __init__(self, project, aliases = None):
		Task.__init__(self, project, aliases)
		self.paths = []
		self.libs = []
		self.static_libs = []
		self.shared_libs = []
		self.flags = []

	def uid(self):
		try: return self._uid
		except AttributeError:
			sig = self._uid = Sig(self.target.path).digest()
			return sig

	def actual_sig(self):
		try: return self._actual_sig
		except AttributeError:
			sig = Sig()
			for t in self.in_tasks: sig.update(t.actual_sig())
			ts = [t.target for t in self.in_tasks]
			for s in self.sources:
				if not s in ts: sig.update(s.sig_to_string())
			sig = self._actual_sig = sig.digest()
			return sig

	def process(self):
		L = []
		for p in self.paths: p += ['-L', p.path]
		l = []
		for l in self.libs: p += ['-l', l]
		return exec_subprocess(['c++', '-o', self.target.path] + [s.path for s in self.sources] + L + l + self.flags)

def exec_subprocess(args, env = None, out_stream = sys.stdout, err_stream = sys.stderr):
	print '======================================================================'
	print ' '.join(args)
	print '______________________________________________________________________'
	p = subprocess.Popen(
		args = args,
		stdout = subprocess.PIPE,
		stderr = subprocess.PIPE,
		env = env
	)
	out, err = p.communicate()
	out_stream.write(out)
	err_stream.write(err)
	return p.returncode
