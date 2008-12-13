#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os

from options import options, help
from logger import out, is_debug, debug, colored
from signature import Sig, raw_to_hexstring
from task import Task, exec_subprocess
from cpp_include_scanner import IncludeScanner

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

	def print_desc(self, desc, color = '7'):
		out.write(colored(color, 'wonderbuild: conf: ' + desc))
		if __debug__ and is_debug: out.write('\n')
		out.flush()
		
	def print_result_desc(self, desc, color = '7'):
		out.write(colored(color, desc))
		out.flush()

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
			sig = Sig(self.prog)
			e = os.environ.get('PKG_CONFIG_PATH', None)
			if e is not None: sig.update(e)
			for f in self.flags: sig.update(f)
			for p in self.pkgs: sig.update(p)
			sig = self._sig = sig.digest()
			return sig

	@property
	def args(self): return self.compiler_args, self.libs_args

	@property
	def compiler_args(self):
		try: return self._compiler_args
		except AttributeError:
			args = [self.prog, '--cflags'] + self.flags + self.pkgs
			self.print_desc(str(args))
			r, out, err = exec_subprocess(args, silent = True)
			self.print_result_desc(' ' + (r == 0 and 'yes' or 'no') + '\n')
			if r != 0: raise Exception, r
			out = out.rstrip('\n').split()
			self._compiler_args = out
			return out

	@property
	def libs_args(self, static = False):
		try: return self._libs_args
		except AttributeError:
			args = [self.prog, '--libs'] + self.flags + self.pkgs
			if static: args.append('--static')
			self.print_desc(str(args))
			r, out, err = exec_subprocess(args, silent = True)
			self.print_result_desc(' ' + (r == 0 and 'yes' or 'no') + '\n')
			if r != 0: raise Exception, r
			out = out.rstrip('\n').split()
			self._libs_args = out
			return out
	
class BaseObjConf(Conf):
	def __init__(self, project): Conf.__init__(self, project)
	
	def help(self):
		help['--cxx'] = ('--cxx=<prog>', 'use <prog> as c++ compiler')
		help['--cxx-flags'] = ('--cxx-flags=[flags]', 'use specific c++ compiler flags')
		help['--cxx-debug'] = ('--cxx-debug=<yes|no>', 'make the c++ compiler produce debugging information or not', 'no')
		help['--cxx-optim'] = ('--cxx-optim=<level>', 'use c++ compiler optimisation <level>')
		help['--cxx-pic'] = ('--cxx-pic=<yes|no>', 'make the c++ compiler emit pic code (for shared libs) rather than non-pic code (for static libs or programs)', 'yes')
	
	def conf(self):
		help['--cxx'] = None
		help['--cxx-flags'] = None
		help['--cxx-debug'] = None
		help['--cxx-optim'] = None
		help['--cxx-pic'] = None

		self.cpp = IncludeScanner(self.project.fs, self.project.state_and_cache)

		try: sig, self.prog, self.flags, self.pic, self.optim, self.debug = self.project.state_and_cache['cxx-compiler']
		except KeyError: parse = True
		else: parse = sig != self.sig
		
		if parse:
			self.pic = True
			self.optim = None
			self.debug = False

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

			self.project.state_and_cache['cxx-compiler'] = self.sig, self.prog, self.flags, self.pic, self.optim, self.debug
			self.check_version()

	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			sig = Sig(str(options))
			sig = self._sig = sig.digest()
			return sig

	def check_version(self):
		color = '34'
		self.print_desc('checking for c++ compiler:', color)
		r, out, err = exec_subprocess([self.prog, '-dumpversion'], silent = True)
		if r != 0:
			self.print_result_desc(' not gcc\n', color)
		else:
			out = out.rstrip('\n')
			self.print_result_desc(' gcc version ' + out + '\n', color)

	@property
	def args(self):
		try: return self._args
		except AttributeError:
			args = [self.prog, '-o', None, None, '-c', '-pipe']
			if self.debug: args.append('-g')
			if self.optim is not None: args.append('-O' + self.optim)
			if self.pic: args.append('-fPIC')
			args += self.flags
			if __debug__ and is_debug: debug('conf: cxx: compiler: ' + str(args))
			self._args = args
			return args

	def paths_args(self, paths, args):
		for p in paths: args += ['-I', p.path]
	
	def defines_args(self, defines, args):
		for k, v in defines.iteritems():
			if v is None: args.append('-D' + k)
			else: args.append('-D' + k + '=' + v)

	def process(self, task):
		dir = task.target.parent
		try:
			dir.lock.acquire()
			dir.make_dir()
		finally: dir.lock.release()
		args = task.conf.args[:]
		args[2] = task.target.path
		args[3] = task.source.path
		if self.pic:
			task.print_desc('compiling pic/shared object from c++ ' + task.source.path + ' -> ' + task.target.path, color = '7;1;34')
		else:
			task.print_desc('compiling non-pic/static object from c++ ' + task.source.path + ' -> ' + task.target.path, color = '7;34')
		r, out, err = exec_subprocess(args)
		if r != 0: raise Exception, r

class BaseModConf(Conf):
	def __init__(self, base_obj_conf):
		Conf.__init__(self, base_obj_conf.project)
		self.base_obj_conf = base_obj_conf

	def help(self):
		help['--mod-shared'] = ('--mod-shared=<yes|no>', 'build shared libs (rather than static libs)', 'yes')
		help['--mod-ld'] = ('--mod-ld=<prog>', 'use <prog> as shared lib and program linker')
		help['--mod-ld-flags'] = ('--mod-ld-flags=[flags]', 'use specific linker flags')
		help['--mod-ar'] = ('--mod-ar=<prog>', 'use <prog> as static lib archiver', 'ar')
		help['--mod-ar-flags'] = ('--mod-ar-flags=[flags]', 'use specific archiver flags', 'cr')
		help['--mod-ranlib'] = ('--mod-ranlib=<prog>', 'use <prog> as static lib archive indexer', 'ranlib')
		help['--mod-ranlib-flags'] = ('--mod-ranlib-flags=[flags]', 'use specific archive indexer flags')

	def conf(self):
		help['--mod-shared'] = None
		help['--mod-ld'] = None
		help['--mod-ld-flags'] = None
		help['--mod-ar'] = None
		help['--mod-ar-flags'] = None
		help['--mod-ranlib'] = None
		help['--mod-ranlib-flags'] = None

		try: sig, self.shared, self.ld_prog, self.ld_flags, self.ar_prog, self.ar_flags, self.ranlib_prog, self.ranlib_flags = self.project.state_and_cache['cxx-module']
		except KeyError: parse = True
		else: parse = sig != self.sig
		
		if parse:
			self.shared = self.base_obj_conf.pic
			
			ld_prog = ld_flags = ar_prog = ar_flags = ranlib_prog = ranlib_flags = False
			for o in options:
				if o.startswith('--mod-shared'): self.shared = o[len('--mod-shared='):] != 'no'
				if o.startswith('--mod-ld='):
					self.ld_prog = o[len('--mod-ld='):]
					ld = True
				elif o.startswith('--mod-ld-flags='):
					self.ld_flags = o[len('--mod-ld-flags='):].split()
					ld_flags = True
				if o.startswith('--mod-ar='):
					self.ar_prog = o[len('--mod-ar='):]
					ar_prog = True
				elif o.startswith('--mod-ar-flags='):
					self.ar_flags = o[len('--mod-ar-flags='):].split()
					ar_flags = True
				if o.startswith('--mod-ranlib='):
					self.ranlib_prog = o[len('--mod-ranlib='):]
					ranlib_prog = True
				elif o.startswith('--mod-ranlib-flags='):
					self.ranlib_flags = o[len('--mod-ranlib-flags='):].split()
					ranlib_flags = True

			if not ld_prog: self.ld_prog = self.base_obj_conf.prog
			if not ld_flags:
				flags = os.environ.get('LDFLAGS', None)
				if flags is not None: self.ld_flags = flags.split()
				else: self.ld_flags = []

			if not ar_prog: self.ar_prog = 'ar'
			if not ar_flags: self.ar_flags = os.environ.get('ARFLAGS', 'cr') # s for gnu to run ranlib
			if not ranlib_prog: self.ranlib_prog = 'ranlib'
			if not ranlib_flags: self.ranlib_flags = os.environ.get('RANLIBFLAGS', None)

			self.project.state_and_cache['cxx-module'] = self.sig, self.shared, self.ld_prog, self.ld_flags, self.ar_prog, self.ar_flags, self.ranlib_prog, self.ranlib_flags

	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			sig = Sig(str(options))
			sig = self._sig = sig.digest()
			return sig

	@property
	def args(self):
		try: return self._args
		except AttributeError:
			if self.shared:
				args = [self.ld_prog, '-o', None, None]
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

	def paths_args(self, paths, args):
		for p in paths: args += ['-L', p.path]
	
	def libs_args(self, libs, static_libs, shared_libs, args):
		for l in libs: args.append('-l' + l)
		if len(static_libs):
			args.append('-Wl,-Bstatic')
			for l in static_libs: args.append('-l' + l)
		if len(static_libs):
			args.append('-Wl,-Bdynamic')
			for l in shared_libs: args.append('-l' + l)

	def target(self, name):
		dir = self.project.bld_node.node_path(os.path.join('modules', name))
		if self.shared: return dir.node_path('lib' + name + '.so')
		else: return dir.node_path('lib' + name + '.a')

	def process(self, task):
		if self.shared:
			args = task.conf.args[:]
			args[2] = task.target.path
			args[3] = [s.path for s in task.sources]
			args = args[:3] + args[3] + args[4:]
			task.print_desc('linking shared lib ' + task.target.path, color = '7;1;36')
			r, out, err = exec_subprocess(args)
			if r != 0: raise Exception, r
		else:
			task.print_desc('archiving and indexing static lib ' + task.target.path, color = '7;36')
			ar_args, ranlib_args = task.conf.args
			args = ar_args[:]
			args.append(task.target.path)
			args += [s.path for s in task.sources]
			r, out, err = exec_subprocess(args)
			if r != 0: raise Exception, r
			args = ranlib_args[:]
			args.append(task.target.path)
			r, out, err = exec_subprocess(args)
			if r != 0: raise Exception, r

class ObjConf(Conf):
	def __init__(self, base_obj_conf):
		Conf.__init__(self, base_obj_conf.project)
		self.base_conf = base_obj_conf
	
	def conf(self):
		self.pkgs = []
		self.paths = []
		self.defines = {}

	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			sig = Sig(self.base_conf.sig)
			e = os.environ.get('CPATH', None)
			if e is not None: sig.update(e)
			e = os.environ.get('CPLUS_INCLUDE_PATH', None)
			if e is not None: sig.update(e)
			for p in self.pkgs: sig.update(p.sig)
			for p in self.paths: sig.update(p.path)
			for k, v in self.defines.iteritems():
				sig.update(k)
				sig.update(v)
			sig = self._sig = sig.digest()
			return sig

	@property
	def args(self):
		try: return self._args
		except AttributeError:
			args = self.base_conf.args[:]
			self.base_conf.paths_args(self.paths, args)
			self.base_conf.defines_args(self.defines, args)
			for p in self.pkgs: args += p.compiler_args
			if __debug__ and is_debug: debug('conf: cxx: obj: ' + str(args))
			self._args = args
			return args

class ModConf(Conf):
	def __init__(self, base_mod_conf, obj_conf):
		Conf.__init__(self, base_mod_conf.project)
		self.base_conf = base_mod_conf
		self.obj_conf = obj_conf

	def conf(self):
		self.pkgs = self.obj_conf.pkgs
		self.paths = []
		self.libs = []
		self.static_libs = []
		self.shared_libs = []

	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			sig = Sig(str(self.base_conf.sig))
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
			args = self.base_conf.args[:]
			self.base_conf.paths_args(self.paths, args)
			self.base_conf.libs_args(self.libs, self.static_libs, self.shared_libs, args)
			if self.base_conf.shared:
				for p in self.pkgs: args += p.libs_args
			if __debug__ and is_debug: debug('conf: cxx: module: ' + str(args))
			self._args = args
			return args

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
			seen, not_found = self.conf.base_conf.cpp.scan_deps(self.source, self.conf.paths)
			for s in seen: sig.update(s.sig)
			sig = self._sig = sig.digest()
			return sig
		
	def process(self): self.conf.base_conf.process(self)

class Mod(Task):
	def __init__(self, mod_conf, name, aliases = None):
		Task.__init__(self, mod_conf.project, aliases)
		self.conf = mod_conf
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

	def dyn_in_tasks(self): self.target = self.conf.base_conf.target(self.name)

	def process(self): self.conf.base_conf.process(self)
		
	def new_obj(self, source):
		obj = Obj(self.obj_conf)
		obj.source = source
		obj.target = self.target.parent.node_path(source.path[:source.path.rfind('.')] + '.o')
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
