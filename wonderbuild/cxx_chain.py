#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os

from options import options, help
from logger import is_debug, debug
from signature import Sig, raw_to_hexstring
from task import Task, exec_subprocess

class Conf(object):
	def __init__(self, project):
		self.project = project
		project.confs.append(self)
		
	def help(self): pass

	def conf(self): pass

	@property
	def sig(self): pass

	@property
	def args(self): pass

class PkgConf(Conf):
	def __init__(self, project):
		Conf.__init__(self, project)
		self.project = project
		self.prog = 'pkg-config'
		self.pkgs = []
		self.flags = []

	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			sig = Sig()
			sig.update(os.environ.get('PKG_CONFIG_PATH', None))
			sig.update(self.prog)
			sig.update(self.flags)
			for p in self.pkgs: sig.update(p)
			sig = self._sig = sig.digest()
			return sig

	@property
	def args(self): return self.compiler_args + self.lib_args

	@property
	def compiler_args(self):
		try: return self._compiler_args
		except AttributeError:
			args = [self.prog, '--cflags'] + self.flags + self.pkgs
			if __debug__ and is_debug: debug('conf: pkg-config: ' + str(args))
			r, out, err = exec_subprocess()
			if r != 0: raise Exception, r
			self._compiler_args = out
			return out

	@property
	def lib_args(self):
		try: return self._lib_args
		except AttributeError:
			args = [self.prog, '--libs'] + self.flags + self.pkgs
			if __debug__ and is_debug: debug('conf: pkg-config: ' + str(args))
			r, out, err = exec_subprocess(args)
			if r != 0: raise Exception, r
			self._lib_args = out
			return args
	
class ObjConf(Conf):
	def __init__(self, project):
		Conf.__init__(self, project)
		self.prog = 'c++'
		self.pkgs = []
		self.paths = []
		self.defines = {}
		self.debug = False
		self.optim = None
		self.pic = True
	
	def help(self):
		help['--cxx-flags'] = ('--cxx-flags=[flags]', 'use specific c++ compiler flags')
		help['--cxx-debug'] = ('--cxx-debug', 'make the c++ compiler produce debug information')
		help['--cxx-optim'] = ('--cxx-optim=<level>', 'use c++ compiler optimisation <level>')
		
	def conf(self):
		help['--cxx-flags'] = None
		help['--cxx-debug'] = None
		help['--cxx-optim'] = None
		self.flags = []
		
		flags = False
		for o in options:
			if o.startswith('--cxx-flags='):
				self.flags += o[len('--cxx-flags='):].split()
				flags = True
			elif o.startswith('--cxx-optim='): self.optim = o[len('--cxx-optim='):]
			elif o == '--cxx-debug': self.debug = True
		
		if not flags:
			flags = os.environ.get('CXXFLAGS', None)
			if flags is not None: self.flags = flags.split()

	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			sig = Sig()
			sig.update(os.environ.get('CPATH', None))
			sig.update(os.environ.get('CPLUS_INCLUDE_PATH', None))
			for p in self.pkgs: sig.update(p.sig)
			for p in self.paths: sig.update(p.sig)
			for f in self.flags: sig.update(f)
			sig.update(self.shared)
			sig = self._sig = sig.digest()
			return sig

	@property
	def args(self):
		try: return self._args
		except AttributeError:
			args = [self.prog, '-o', None, None, '-c', '-pipe']
			for p in self.pkgs: args += p.compiler_args
			for p in self.paths: args += ['-I', p.path]
			for k, v in self.defines.iteritems():
				if v is None: args.append('-D' + k)
				else: args.append('-D' + k + '=' + v)
			if self.debug: args.append('-g')
			if self.optim is not None: args.append('-O' + self.optim)
			if self.pic: args.append('-fPIC')
			args += self.flags
			if __debug__ and is_debug: debug('conf: cxx: obj: ' + str(args))
			self._args = args
			return args

	def process(self, target, source):
		dir = target.parent
		try:
			dir.lock.acquire()
			dir.make_dir()
		finally: dir.lock.release()
		args = self.args[:]
		args[2] = target.path
		args[3] = source.path
		r, out, err = exec_subprocess(args, desc = 'compiling c++ ' + target.path, color = '4')
		if r != 0: raise Exception, r
			
class Obj(Task):
	def __init__(self, obj_conf):
		Task.__init__(self, obj_conf.project)
		self.conf = obj_conf
		self.source = None
		self.target = None
		
	@property
	def uid(self):
		try: return self._uid
		except AttributeError:
			sig = self._uid = Sig(self.target.path).digest()
			return sig

	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			sig = self._sig = self.source.sig_to_string()
			return sig
		
	def process(self): self.conf.process(self.target, self.source)

class LibConf(Conf):
	def __init__(self, obj_conf):
		Conf.__init__(self, obj_conf.project)
		self.obj_conf = obj_conf
		self.prog = obj_conf.prog
		self.shared = obj_conf.pic
		self.pkgs = obj_conf.pkgs
		self.paths = []
		self.libs = []
		self.static_libs = []
		self.shared_libs = []

	def help(self):
		help['--ld-flags'] = ('--ld-flags=[flags]', 'use specific linker flags')

	def conf(self):
		help['--ld-flags'] = None
		self.flags = []
		
		opt = False
		for o in options:
			if o.startswith('--ld-flags='):
				self.flags += o[len('-ld-flags='):].split()
				opt = True
		
		if not opt:
			flags = os.environ.get('LDFLAGS', None)
			if flags is not None: self.flags = flags.split()

	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			sig = Sig()
			for p in self.pkgs: sig.update(p.sig)
			for p in self.paths: sig.update(p.sig)
			for l in self.libs: sig.update(l)
			for l in self.static_libs: sig.update(l)
			for l in self.shared_libs: sig.update(l)
			for f in self.flags: sig.update(f)
			sig = self._sig = sig.digest()
			return sig

	@property
	def args(self):
		try: return self._args
		except AttributeError:
			if self.shared:
				args = [self.prog, '-o', None, []]
				for p in self.pkgs: args += p.lib_args
				for p in self.paths: args += ['-L', p.path]
				for l in self.libs: args.append('-l' + l)
				if len(self.static_libs):
					args.append('-Wl,-Bstatic')
					for l in self.static_libs: args.append('-l' + l)
				if len(self.static_libs):
					args.append('-Wl,-Bdynamic')
					for l in self.static_libs: args.append('-l' + l)
				if self.shared: args.append('-shared')
				args += self.flags
				if __debug__ and is_debug: debug('conf: cxx: lib: ' + str(args))
				self._args = args
				return args
			else: pass #TODO ar, ranlib

	def process(self, target, sources):
		if self.shared:
			args = self.args[:]
			args[2] = target.path
			args[3] = [s.path for s in sources]
			args = args[:3] + args[3] + args[4:]
			r, out, err = exec_subprocess(args, desc = 'linking c++ ' + target.path, color = '6')
			if r != 0: raise Exception, r
		else: pass #TODO ar, ranlib

class Lib(Task):
	def __init__(self, lib_conf, aliases = None):
		Task.__init__(self, lib_conf.project, aliases)
		self.conf = lib_conf
		self.target = None
		self.sources = []

	@property
	def obj_conf(self): return self.conf.obj_conf

	@property
	def uid(self):
		try: return self._uid
		except AttributeError:
			sig = self._uid = Sig(self.target.path).digest()
			return sig

	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			sig = Sig()
			for t in self.in_tasks: sig.update(t.sig)
			ts = [t.target for t in self.in_tasks]
			for s in self.sources:
				if s not in ts: sig.update(s.sig_to_string())
			sig = self._sig = sig.digest()
			return sig

	def process(self): self.conf.process(self.target, self.sources)
		
	def new_obj(self, source):
		obj = Obj(self.obj_conf)
		obj.source = source
		obj.target = self.target.parent.rel_node(source.path[:source.path.rfind('.')] + '.o')
		self.add_in_task(obj)
		self.sources.append(obj.target)
		return obj

class Contexes(object):
	def check_and_build(self):
		'when performing build checks, or building the sources'
		pass
	
	def build(self):
		'when building the sources'
		pass
	
	class client:
		'when used as a dependency'
		pass
