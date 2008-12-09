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
	
	def help(self):
		help['--cxx'] = ('--cxx=<prog>', 'use <prog> as c++ compiler')
		help['--cxx-flags'] = ('--cxx-flags=[flags]', 'use specific c++ compiler flags')
		help['--cxx-debug'] = ('--cxx-debug=<yes|no>', 'make the c++ compiler produce debugging information or not', 'no')
		help['--cxx-optim'] = ('--cxx-optim=<level>', 'use c++ compiler optimisation <level>')
		help['--cxx-pic'] = ('--cxx-pic=<yes|no>', 'make the c++ compiler emit pic code (for shared libs) or non-pic code (for static libs or programs)', 'yes')
		
	def conf(self):
		self.cpp = self.project.cpp
		self.pic = True
		self.optim = None
		self.debug = False
		self.pkgs = []
		self.paths = []
		self.defines = {}

		help['--cxx'] = None
		help['--cxx-flags'] = None
		help['--cxx-debug'] = None
		help['--cxx-optim'] = None
		help['--cxx-pic'] = None
		help['--cxx-non-pic'] = None

		prog = flags = False
		for o in options:
			if o.startswith('--cxx='):
				self.prog = o[len('--cxx='):]
				prog = True
			elif o.startswith('--cxx-flags='):
				self.flags = o[len('--cxx-flags='):].split()
				flags = True
			elif o.startswith('--cxx-pic='): self.pic = o[len('--cxx-pic='):] != 'no'
			elif o.startswith('--cxx-optim='): self.optim = o[len('--cxx-optim='):]
			elif o.startswith('--cxx-debug='): self.debug = o[len('--cxx-debug='):] == 'yes'
		
		if not prog: self.prog = os.environ.get('CXX', 'c++')
		if not flags:
			flags = os.environ.get('CXXFLAGS', None)
			if flags is not None: self.flags = flags.split()
			else: self.flags = []

	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			sig = Sig(self.prog)
			e = os.environ.get('CPATH', None)
			if e is not None: sig.update(e)
			e = os.environ.get('CPLUS_INCLUDE_PATH', None)
			if e is not None: sig.update(e)
			sig.update(str(self.pic))
			sig.update(str(self.optim))
			sig.update(str(self.debug))
			for p in self.pkgs: sig.update(p.sig)
			for p in self.paths: sig.update(p.path)
			for k, v in self.defines.iteritems():
				sig.update(k)
				sig.update(v)
			for f in self.flags: sig.update(f)
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
		if self.pic:
			r, out, err = exec_subprocess(args, desc = 'compiling pic/shared object from c++ ' + source.path + ' -> ' + target.path, color = '7;1;34')
		else:
			r, out, err = exec_subprocess(args, desc = 'compiling non-pic/static object from c++ ' + source.path + ' -> ' + target.path, color = '7;34')
		if r != 0: raise Exception, r
			
class Obj(Task):
	def __init__(self, obj_conf):
		Task.__init__(self, obj_conf.project)
		self.conf = obj_conf
		self.source = None
		self.target = None

	@property
	def uid(self): return self.target

	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			sig = Sig(self.conf.sig)
			sig.update(self.source.sig)
			seen, not_found = self.conf.cpp.scan_deps(self.source, self.conf.paths)
			for s in seen: sig.update(s.sig)
			sig = self._sig = sig.digest()
			return sig
		
	def process(self): self.conf.process(self.target, self.source)

class LibConf(Conf):
	def __init__(self, obj_conf):
		Conf.__init__(self, obj_conf.project)
		self.obj_conf = obj_conf

	def help(self):
		help['--lib-shared'] = ('--lib-shared=<yes|no>', 'build shared libs (rather than static libs)', 'yes')
		help['--lib-ld'] = ('--lib-ld=<prog>', 'use <prog> as shared lib and program linker')
		help['--lib-ld-flags'] = ('--lib-ld-flags=[flags]', 'use specific linker flags')
		help['--lib-ar'] = ('--lib-ar=<prog>', 'use <prog> as static lib archiver', 'ar')
		help['--lib-ar-flags'] = ('--lib-ar-flags=[flags]', 'use specific archiver flags', 'cr')
		help['--lib-ranlib'] = ('--lib-ranlib=<prog>', 'use <prog> as static lib archive indexer', 'ranlib')
		help['--lib-ranlib-flags'] = ('--lib-ranlib-flags=[flags]', 'use specific archive indexer flags')

	def conf(self):
		self.shared = self.obj_conf.pic
		self.pkgs = self.obj_conf.pkgs
		self.paths = []
		self.libs = []
		self.static_libs = []
		self.shared_libs = []

		help['--lib-shared'] = None
		help['--lib-ld'] = None
		help['--lib-ld-flags'] = None
		help['--lib-ar'] = None
		help['--lib-ar-flags'] = None
		help['--lib-ranlib'] = None
		help['--lib-ranlib-flags'] = None

		ld_prog = ld_flags = ar_prog = ar_flags = ranlib_prog = ranlib_flags = False
		for o in options:
			if o.startswith('--lib-shared'): self.shared = o[len('--lib-shared='):] != 'no'
			if o.startswith('--lib-ld='):
				self.ld_prog = o[len('--lib-ld='):]
				ld = True
			elif o.startswith('--lib-ld-flags='):
				self.ld_flags = o[len('--lib-ld-flags='):].split()
				ld_flags = True
			if o.startswith('--lib-ar='):
				self.ar_prog = o[len('--lib-ar='):]
				ar_prog = True
			elif o.startswith('--lib-ar-flags='):
				self.ar_flags = o[len('--lib-ar-flags='):].split()
				ar_flags = True
			if o.startswith('--lib-ranlib='):
				self.ranlib_prog = o[len('--lib-ranlib='):]
				ranlib_prog = True
			elif o.startswith('--lib-ranlib-flags='):
				self.ranlib_flags = o[len('--lib-ranlib-flags='):].split()
				ranlib_flags = True
		if self.shared:
			if not ld_prog: self.ld_prog = self.obj_conf.prog
			if not ld_flags:
				flags = os.environ.get('LDFLAGS', None)
				if flags is not None: self.ld_flags = flags.split()
				else: self.ld_flags = []
		else:
			if not ar_prog: self.ar_prog = 'ar'
			if not ar_flags: self.ar_flags = os.environ.get('ARFLAGS', 'cr') # s for gnu to run ranlib
			if not ranlib_prog: self.ranlib_prog = 'ranlib'
			if not ranlib_flags: self.ranlib_flags = os.environ.get('RANLIBFLAGS', None)

	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			sig = Sig(str(self.shared))
			if self.shared:
				sig.update(self.ld_prog)
				for f in self.ld_flags: sig.update(f)
			else:
				sig.update(self.ar_prog)
				if self.ar_flags is not None: sig.update(self.ar_flags)
				sig.update(self.ranlib_prog)
				if self.ranlib_flags is not None: sig.update(self.ranlib_flags)
			for p in self.pkgs: sig.update(p.sig)
			for p in self.paths: sig.update(p.path)
			for l in self.libs: sig.update(l)
			for l in self.static_libs: sig.update(l)
			for l in self.shared_libs: sig.update(l)
			sig = self._sig = sig.digest()
			return sig

	@property
	def args(self):
		try: return self._args
		except AttributeError:
			if self.shared:
				args = [self.ld_prog, '-o', None, []]
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
				args += self.ld_flags
				if __debug__ and is_debug: debug('conf: cxx: ld: ' + str(args))
				self._args = args
				return args
			else:
				ar_args = [self.ar_prog]
				if self.ar_flags is not None: ar_args.append(self.ar_flags)
				if __debug__ and is_debug: debug('conf: cxx: ar: ' + str(ar_args))
				ranlib_args = [self.ranlib_prog]
				if self.ranlib_flags is not None: ranlib_args.append(self.ranlib_flags)
				if __debug__ and is_debug: debug('conf: cxx: ranlib: ' + str(ranlib_args))
				args = self._args = ar_args, ranlib_args
				return args

	def target(self, name):
		dir = self.project.bld_node.rel_node(os.path.join('modules', name))
		if self.shared: return dir.rel_node('lib' + name + '.so')
		else: return dir.rel_node('lib' + name + '.a')

	def process(self, target, sources):
		if self.shared:
			args = self.args[:]
			args[2] = target.path
			args[3] = [s.path for s in sources]
			args = args[:3] + args[3] + args[4:]
			r, out, err = exec_subprocess(args, desc = 'linking shared lib ' + target.path, color = '7;1;36')
			if r != 0: raise Exception, r
		else:
			ar_args, ranlib_args = self.args
			
			args = ar_args[:]
			args.append(target.path)
			args += [s.path for s in sources]
			r, out, err = exec_subprocess(args, desc = 'archiving static lib ' + target.path, color = '7;36')
			if r != 0: raise Exception, r

			args = ranlib_args[:]
			args.append(target.path)
			r, out, err = exec_subprocess(args, desc = ' indexing static lib ' + target.path, color = '7;36')
			if r != 0: raise Exception, r

class Lib(Task):
	def __init__(self, lib_conf, name, aliases = None):
		Task.__init__(self, lib_conf.project, aliases)
		self.conf = lib_conf
		self.name = name
		self.target = None
		self.sources = []

	@property
	def obj_conf(self): return self.conf.obj_conf

	@property
	def uid(self): return self.target

	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			sig = Sig(self.conf.sig)
			for t in self.in_tasks: sig.update(t.sig)
			ts = [t.target for t in self.in_tasks]
			for s in self.sources:
				if s not in ts: sig.update(s.sig)
			sig = self._sig = sig.digest()
			return sig

	def dyn_in_tasks(self): self.target = self.conf.target(self.name)

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
