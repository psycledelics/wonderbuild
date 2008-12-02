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
	
	@property
	def uid(self): return None
	
	@property
	def old_sig(self):
		try: return self.project.task_sigs[self.uid]
		except KeyError: return None
	
	@property
	def actual_sig(self): return None
	
	def update_sig(self): self.project.task_sigs[self.uid] = self.actual_sig
	
class CxxObj(Task):
	def __init__(self, project):
		Task.__init__(self, project)
		self.source = None
		self.target = None
		self.paths = []
		self.defines = {}
		self.debug = False
		self.optim = None
		self.pic = True
		self.flags = os.environ.get('CXXFLAGS', [])
		
	@property
	def uid(self):
		try: return self._uid
		except AttributeError:
			sig = self._uid = Sig(self.target.path).digest()
			return sig

	@property
	def actual_sig(self):
		try: return self._actual_sig
		except AttributeError:
			sig = self._actual_sig = self.source.sig_to_string()
			return sig
		
	def process(self):
		self.target.parent.make_dir()
		args = ['c++', '-o', self.target.path, self.source.path, '-c', '-pipe']
		if len(self.paths):
			for p in self.paths: args += ['-I', p.path]
		if len(self.defines):
			for k, v in self.defines.iteritems():
				if v is None: args.append('-D' + k)
				else: args.append('-D' + k + '=' + v)
		if self.debug: args.append('-g')
		if self.optim is not None: args.append('-O' + str(self.optim))
		if self.pic: args.append('-fPIC')
		return exec_subprocess(args + self.flags)

class Lib(Task):
	def __init__(self, project, aliases = None):
		Task.__init__(self, project, aliases)
		self.paths = []
		self.libs = []
		self.static_libs = []
		self.shared_libs = []
		self.shared = True
		self.flags = os.environ.get('LDFLAGS', [])

	@property
	def uid(self):
		try: return self._uid
		except AttributeError:
			sig = self._uid = Sig(self.target.path).digest()
			return sig

	@property
	def actual_sig(self):
		try: return self._actual_sig
		except AttributeError:
			sig = Sig()
			for t in self.in_tasks: sig.update(t.actual_sig)
			ts = [t.target for t in self.in_tasks]
			for s in self.sources:
				if not s in ts: sig.update(s.sig_to_string())
			sig = self._actual_sig = sig.digest()
			return sig

	def process(self):
		args = ['c++', '-o', self.target.path] + [s.path for s in self.sources]
		if len(self.paths):
			for p in self.paths: args += ['-L', p.path]
		if len(self.libs):
			for l in self.libs: args.append('-l' + l)
		if len(self.static_libs):
			args.append('-Wl,-B,-static')
			for l in self.static_libs: args.append('-l' + l)
		if len(self.static_libs):
			args.append('-Wl,-B,-dynamic')
			for l in self.static_libs: args.append('-l' + l)
		if self.shared: args.append('-shared')
		return exec_subprocess(args + self.flags)

class LibCxxObj(CxxObj):
	def __init__(self, lib, source):
		CxxObj.__init__(self, lib.project)
		self.source = source
		path = lib.project.src_node.path_to(source)
		path = path[:path.rfind('.')] + '.o'
		self.target = lib.target.parent.rel_node(path)
		self.add_out_task(lib)
		lib.sources.append(self.target)

class CxxLib(Lib):
	def __init__(self, project, aliases):
		Lib.__init__(self, project, aliases)
		self.sources = []
		self.cxx_paths = []
		self.defines = {}
		self.debug = False
		self.optim = None
		self.cxx_flags = os.environ.get('CXXFLAGS', [])

	def dyn_in_tasks(self):
		if len(self.in_tasks): return None
		for s in self.sources:
			o = LibCxxObj(self, s)
			o.paths = self.cxx_paths
			o.defines = self.defines
			o.debug = self.debug
			o.optim = self.optim
			o.flags = self.cxx_flags
		return self.in_tasks

def exec_subprocess(args, env = None, out_stream = sys.stdout, err_stream = sys.stderr):
	print '=' * 79
	print ' '.join(args)
	print '_' * 79
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
