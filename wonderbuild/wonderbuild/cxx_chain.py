#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2007-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os, threading
#python 2.5.0a1 from __future__ import with_statement

from options import options, known_options, help
from logger import out, is_debug, debug, colored, silent
from signature import Sig
from task import Task, exec_subprocess, exec_subprocess_pipe
from cpp_include_scanner import IncludeScanner

class Cfg(object):
	def __init__(self, project):
		self.project = project
		project.cfgs.append(self)
		self.lock = threading.Lock()

	def options(self): pass
		
	def help(self): pass

	def configure(self): pass

	@property
	def sig(self): raise Exception, str(self.__class__) + ' must implement the sig property'

	@property
	def args(self): pass

	def print_desc(self, desc, color = '34'):
		if silent: return
		out.write(colored(color, 'wonderbuild: cfg: ' + desc + ':') + ' ')
		if __debug__ and is_debug: out.write('\n')
		out.flush()
		
	def print_result_desc(self, desc, color = '34'):
		if silent: return
		out.write(colored(color, desc))
		out.flush()

class PkgCfg(Cfg):
	def __init__(self, project):
		Cfg.__init__(self, project)
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
		self.lock.acquire()
		try:
			try: return self._compiler_args
			except AttributeError:
				args = [self.prog, '--cflags'] + self.flags + self.pkgs
				if not silent: self.print_desc('getting pkg-config compile flags: ' + ' '.join(self.pkgs))
				r, out, err = exec_subprocess_pipe(args, silent = True)
				if r != 0: 
					self.print_result_desc('error\n', color = '31')
					raise Exception, r
				self.print_result_desc('ok\n', color = '32')
				out = out.rstrip('\n').split()
				self._compiler_args = out
				return out
		finally: self.lock.release()

	@property
	def libs_args(self, static = False):
		self.lock.acquire()
		try:
			try: return self._libs_args
			except AttributeError:
				args = [self.prog, '--libs'] + self.flags + self.pkgs
				if static:
					args.append('--static')
					if not silent: self.print_desc('getting pkg-config static libs: ' + ' '.join(self.pkgs))
				elif not silent: self.print_desc('getting pkg-config shared libs: ' + ' '.join(self.pkgs))
				r, out, err = exec_subprocess_pipe(args, silent = True)
				if r != 0: 
					if not silent: self.print_result_desc('error\n', color = '31')
					raise Exception, r
				if not silent: self.print_result_desc('ok\n', color = '32')
				out = out.rstrip('\n').split()
				self._libs_args = out
				return out
		finally: self.lock.release()
	
class BaseCxxCfg(Cfg):
	_options = set(['--cxx', '--cxx-flags', '--cxx-debug', '--cxx-optim', '--cxx-pic'])
	
	def options(self):
		global known_options
		known_options |= self.__class__._options

	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			sig = Sig()
			for o in options:
				for oo in self.__class__._options:
					if o.startswith(oo + '='): sig.update(o)
			sig = self._sig = sig.digest()
			return sig

	def help(self):
		help['--cxx']       = ('--cxx=<prog>', 'use <prog> as c++ compiler')
		help['--cxx-flags'] = ('--cxx-flags=[flags]', 'use specific c++ compiler flags')
		help['--cxx-debug'] = ('--cxx-debug=<yes|no>', 'make the c++ compiler produce debugging information or not', 'no')
		help['--cxx-optim'] = ('--cxx-optim=<level>', 'use c++ compiler optimisation <level>')
		help['--cxx-pic']   = ('--cxx-pic=<yes|no>', 'make the c++ compiler emit pic code (for shared libs) rather than non-pic code (for static libs or programs)', 'yes')
	
	def configure(self):
		self.cpp = IncludeScanner(self.project.state_and_cache)

		try: sig, self.prog, self.flags, self.pic, self.optim, self.debug, self.kind, self.version, self.__args = self.project.state_and_cache['cxx-compiler']
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

			self._check_kind_and_version()
			if self.kind == 'gcc': self._args = self._gcc_args
			else: raise Exception, 'unsupported c++ compiler'
			self.project.state_and_cache['cxx-compiler'] = self.sig, self.prog, self.flags, self.pic, self.optim, self.debug, self.kind, self.version, self.args

		if self.kind == 'gcc':
			self.pic_args = self._gcc_pic_args
			self.paths_args = self._posix_paths_args
			self.defines_args = self._posix_defines_args
		else: raise Exception, 'unsupported c++ compiler'

	def _check_kind_and_version(self):
		if not silent: self.print_desc('checking for c++ compiler')
		r, out, err = exec_subprocess_pipe([self.prog, '-dumpversion'], silent = True)
		if r != 0:
			if not silent: self.print_result_desc('not gcc\n', '31')
			self.kind = None
			self.version = None
		else:
			self.kind = 'gcc'
			self.version = out.rstrip('\n')
		if not silent: self.print_result_desc(self.kind + ' version ' + self.version + '\n', '32')
	
	@property
	def args(self):
		try: return self.__args
		except AttributeError:
			args = self.__args = self._args()
			if __debug__ and is_debug: debug('cfg: cxx: compiler: ' + str(args))
			return args

	def _gcc_args(self):
		args = [self.prog, '-o', None, None, '-c', '-pipe']
		if self.debug: args.append('-g')
		if self.optim is not None: args.append('-O' + self.optim)
		args += self.flags
		return args

	@staticmethod
	def _gcc_pic_args(pic, args):
		if pic: args.append('-fPIC')
	
	@staticmethod
	def _posix_paths_args(paths, args):
		for p in paths: args += ['-I', p.path]

	@staticmethod
	def _posix_defines_args(defines, args):
		for k, v in defines.iteritems():
			if v is None: args.append('-D' + k)
			else: args.append('-D' + k + '=' + v)

	@staticmethod
	def _read_gcc_dep_file(target, dep_rel):
		'''reads deps from a .d file generated as side-effect of compilation by gcc's -MD or -MMD option'''
		
		path = target.path[:target.path.rfind('.')] + '.d'
		f = open(path, 'rb')
		try: deps = f.read()
		finally: f.close()
		deps = deps.replace('\\\n', '')
		deps = deps[deps.find(':') + 1:].split()
		deps = [dep_rel.node_path(dep) for dep in deps]
		if __debug__ and is_debug: debug('cpp: gcc dep file: ' + path + ': ' + str([str(d) for d in deps]))
		return deps

	def process(self, cxx_task):
		dir = cxx_task.target.parent
		lock = dir.lock
		try:
			lock.acquire()
			dir.make_dir()
		finally: lock.release()
		args = cxx_task.cfg.args[:]
		args[2] = cxx_task.target.path
		args[3] = cxx_task.source.path
		if not silent:
			if cxx_task.cfg.pic:
				cxx_task.print_desc('compiling pic/shared object from c++ ' + cxx_task.source.path + ' -> ' + cxx_task.target.path, color = '7;1;34')
			else:
				cxx_task.print_desc('compiling non-pic/static object from c++ ' + cxx_task.source.path + ' -> ' + cxx_task.target.path, color = '7;34')
		r = exec_subprocess(args)
		if r != 0: raise Exception, r

class BaseModCfg(Cfg):
	def __init__(self, base_cxx_cfg):
		Cfg.__init__(self, base_cxx_cfg.project)
		self.base_cxx_cfg = base_cxx_cfg

	_options = set([
		'--cxx-mod-shared',
		'--cxx-mod-ld', '--cxx-mod-ld-flags',
		'--cxx-mod-ar', '--cxx-mod-ar-flags',
		'--cxx-mod-ranlib', '--cxx-mod-ranlib-flags'
	])
	
	def options(self):
		global known_options
		known_options |= self.__class__._options

	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			sig = Sig(self.base_cxx_cfg.sig)
			for o in options:
				for oo in self.__class__._options:
					if o.startswith(oo + '='): sig.update(o)
			sig = self._sig = sig.digest()
			return sig

	def help(self):
		help['--cxx-mod-shared']       = ('--cxx-mod-shared=<yes|no>', 'build and link shared libs (rather than static libs)', 'yes')
		help['--cxx-mod-ld']           = ('--cxx-mod-ld=<prog>', 'use <prog> as shared lib and program linker')
		help['--cxx-mod-ld-flags']     = ('--cxx-mod-ld-flags=[flags]', 'use specific linker flags')
		help['--cxx-mod-ar']           = ('--cxx-mod-ar=<prog>', 'use <prog> as static lib archiver', 'ar')
		help['--cxx-mod-ar-flags']     = ('--cxx-mod-ar-flags=[flags]', 'use specific archiver flags', 'rc')
		help['--cxx-mod-ranlib']       = ('--cxx-mod-ranlib=<prog>', 'use <prog> as static lib archive indexer', 'ranlib')
		help['--cxx-mod-ranlib-flags'] = ('--cxx-mod-ranlib-flags=[flags]', 'use specific archive indexer flags')

	def configure(self):
		try: sig, self.shared, self.ld_prog, self.ld_flags, self.ar_prog, self.ar_flags, self.ranlib_prog, self.ranlib_flags, self.__args = self.project.state_and_cache['cxx-module']
		except KeyError: parse = True
		else: parse = sig != self.sig
	
		if parse:
			self.shared = self.base_cxx_cfg.pic
		
			ld_prog = ld_flags = ar_prog = ar_flags = ranlib_prog = ranlib_flags = False
			for o in options:
				if o.startswith('--cxx-mod-shared'): self.shared = o[len('--cxx-mod-shared='):] != 'no'
				if o.startswith('--cxx-mod-ld='):
					self.ld_prog = o[len('--cxx-mod-ld='):]
					ld = True
				elif o.startswith('--cxx-mod-ld-flags='):
					self.ld_flags = o[len('--cxx-mod-ld-flags='):].split()
					ld_flags = True
				if o.startswith('--cxx-mod-ar='):
					self.ar_prog = o[len('--cxx-mod-ar='):]
					ar_prog = True
				elif o.startswith('--cxx-mod-ar-flags='):
					self.ar_flags = o[len('--cxx-mod-ar-flags='):].split()
					ar_flags = True
				if o.startswith('--cxx-mod-ranlib='):
					self.ranlib_prog = o[len('--cxx-mod-ranlib='):]
					ranlib_prog = True
				elif o.startswith('--cxx-mod-ranlib-flags='):
					self.ranlib_flags = o[len('--cxx-mod-ranlib-flags='):].split()
					ranlib_flags = True

			if not ld_prog: self.ld_prog = self.base_cxx_cfg.prog
			if not ld_flags:
				flags = os.environ.get('LDFLAGS', None)
				if flags is not None: self.ld_flags = flags.split()
				else: self.ld_flags = []

			if not ar_prog: self.ar_prog = 'ar'
			if not ar_flags:
				self.ar_flags = os.environ.get('ARFLAGS', None)
				if self.ar_flags is None:
					if self.base_cxx_cfg.kind == 'gcc': self.ar_flags = 'rcus'
					else: self.ar_flags = 'rc'
					
			if not ranlib_prog: self.ranlib_prog = 'ranlib'
			if not ranlib_flags: self.ranlib_flags = os.environ.get('RANLIBFLAGS', None)

			if self.base_cxx_cfg.kind == 'gcc': self._args = self._gcc_args
			else: raise Exception, 'unsupported lib archiver/linker'
			self.project.state_and_cache['cxx-module'] = self.sig, self.shared, self.ld_prog, self.ld_flags, self.ar_prog, self.ar_flags, self.ranlib_prog, self.ranlib_flags, self.args

		if self.base_cxx_cfg.kind == 'gcc':
			self.shared_args = self._gcc_shared_args
			self.paths_args = self._posix_paths_args
			self.libs_args = self._gcc_libs_args
			self.ar_flags = 'rcs'
			self.target = self._linux_target
		else: raise Exception, 'unsupported lib archiver/linker'

	@property
	def args(self):
		try: return self.__args
		except AttributeError:
			args = self.__args = self._args()
			return args

	def _gcc_args(self):
		ld_args = [self.ld_prog, '-o', None, None] + self.ld_flags
		if __debug__ and is_debug: debug('cfg: cxx: ld: ' + str(ld_args))

		ar_args = [self.ar_prog]
		if self.ar_flags is not None: ar_args.append(self.ar_flags)
		if __debug__ and is_debug: debug('cfg: cxx: ar: ' + str(ar_args))

		ranlib_args = [self.ranlib_prog]
		if self.ranlib_flags is not None: ranlib_args.append(self.ranlib_flags)
		if __debug__ and is_debug: debug('cfg: cxx: ranlib: ' + str(ranlib_args))

		return ld_args, ar_args, ranlib_args

	@staticmethod
	def _gcc_shared_args(shared, args):
		if shared: args.append('-shared')

	@staticmethod
	def _posix_paths_args(paths, args):
		for p in paths: args += ['-L', p.path]
	
	@staticmethod
	def _gcc_libs_args(libs, static_libs, shared_libs, args):
		for l in libs: args.append('-l' + l)
		if len(static_libs):
			args.append('-Wl,-Bstatic')
			for l in static_libs: args.append('-l' + l)
		if len(static_libs):
			args.append('-Wl,-Bdynamic')
			for l in shared_libs: args.append('-l' + l)

	@staticmethod
	def _linux_target(mod_task):
		dir = mod_task.project.bld_node.node_path(os.path.join('modules', mod_task.name))
		if mod_task.cfg.kind == 'prog': name = mod_task.name
		else:
			name = 'lib' + mod_task.name
			if mod_task.cfg.shared: name += '.so'
			else: name += '.a'
		return dir.node_path(name)

	def process(self, mod_task):
		if mod_task.cfg.ld:
			args = mod_task.cfg.args[:]
			args[2] = mod_task.target.path
			args[3] = [s.path for s in mod_task.sources]
			args = args[:3] + args[3] + args[4:]
			if not silent:
				if mod_task.cfg.kind == 'prog':
					mod_task.print_desc('linking program ' + mod_task.target.path, color = '7;1;32')
				elif mod_task.cfg.kind == 'loadable':
					mod_task.print_desc('linking loadable module ' + mod_task.target.path, color = '7;1;34')
				else:
					mod_task.print_desc('linking shared lib ' + mod_task.target.path, color = '7;1;33')
			r = exec_subprocess(args)
			if r != 0: raise Exception, r
		else:
			if not silent: mod_task.print_desc('archiving and indexing static lib ' + mod_task.target.path, color = '7;36')
			ar_args, ranlib_args = mod_task.cfg.args
			args = ar_args[:]
			args.append(mod_task.target.path)
			args += [s.path for s in mod_task.sources]
			r = exec_subprocess(args)
			if r != 0: raise Exception, r
			if 's' not in self.ar_flags:
				args = ranlib_args[:]
				args.append(mod_task.target.path)
				r = exec_subprocess(args)
				if r != 0: raise Exception, r

class CxxCfg(Cfg):
	def __init__(self, base_cxx_cfg):
		Cfg.__init__(self, base_cxx_cfg.project)
		self.base_cfg = base_cxx_cfg
	
	def configure(self):
		self.pic = self.base_cfg.pic
		self.pkgs = []
		self.paths = []
		self.defines = {}

	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			sig = Sig(self.base_cfg.sig)
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
		self.lock.acquire()
		try:
			try: return self._args
			except AttributeError:
				args = self.base_cfg.args[:]
				self.base_cfg.pic_args(self.pic, args)
				self.base_cfg.paths_args(self.paths, args)
				self.base_cfg.defines_args(self.defines, args)
				for p in self.pkgs: args += p.compiler_args
				if __debug__ and is_debug: debug('cfg: cxx: ' + str(args))
				self._args = args
				return args
		finally: self.lock.release()

class ModCfg(Cfg):
	def __init__(self, base_mod_cfg, cxx_cfg, kind):
		Cfg.__init__(self, base_mod_cfg.project)
		self.base_cfg = base_mod_cfg
		self.cxx_cfg = cxx_cfg
		self.kind = kind

	def configure(self):
		if self.kind == 'prog':
			self.shared = False
			self.ld = True
		else:
			self.shared = self.base_cfg.shared
			self.ld = self.shared
			if self.shared and not self.cxx_cfg.pic:
				debug('cfg: cxx: module: overriding cxx cfg to pic')
				self.cxx_cfg.pic = True
		self.pkgs = self.cxx_cfg.pkgs
		self.paths = []
		self.libs = []
		self.static_libs = []
		self.shared_libs = []

	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			sig = Sig(str(self.base_cfg.sig))
			for p in self.pkgs: sig.update(p.sig)
			for p in self.paths: sig.update(p.path)
			for l in self.libs: sig.update(l)
			for l in self.static_libs: sig.update(l)
			for l in self.shared_libs: sig.update(l)
			sig = self._sig = sig.digest()
			return sig

	@property
	def args(self):
		self.lock.acquire()
		try:
			try: return self._args
			except AttributeError:
				ld_args, ar_args, ranlib_args = self.base_cfg.args
				if not self.ld:
					args = ar_args, ranlib_args
				else:
					args = ld_args[:]
					self.base_cfg.shared_args(self.shared, args)
					self.base_cfg.paths_args(self.paths, args)
					self.base_cfg.libs_args(self.libs, self.static_libs, self.shared_libs, args)
					for p in self.pkgs: args += p.libs_args
				if __debug__ and is_debug: debug('cfg: cxx: module: ' + str(args))
				self._args = args
				return args
		finally: self.lock.release()

class CxxTask(Task):
	def __init__(self, cxx_cfg):
		Task.__init__(self, cxx_cfg.project)
		self.cfg = cxx_cfg
		self.source = None
		self.target = None

	def __str__(self): return str(self.target)

	@property
	def uid(self): return self.target

	@property
	def old_sig(self):
		try: return self.project.task_states[self.uid][0]
		except KeyError: return None

	if False: # gcc deps (fastest)
		def process(self):
			self.cfg.base_cfg.process(self)
			implicit_deps = self.cfg.base_cfg._read_gcc_dep_file(self.target, self.project.fs.cur)
			sigs = [s.sig for s in implicit_deps]
			sigs.sort()
			sig = Sig(self.cfg.sig)
			sig.update(''.join(sigs))
			sig = sig.digest()
			self._sig = sig
			self.project.task_states[self.uid] = (sig, implicit_deps)
			Task.process(self)

		def post_process(self): pass # already done in a thread-safe way in process()

		@property
		def sig(self):
			try: return self._sig
			except AttributeError:
				try: old_sig, implicit_deps = self.project.task_states[self.uid]
				except KeyError:
					self._sig = 0
					return self._sig
				else:
					try: sigs = [s.sig for s in implicit_deps]
					except OSError:
						# A cached implicit dep does not exist anymore.
						# We must recompute the implicit deps.
						if __debug__ and is_debug: debug('cpp: deps not found: ' + self.source.path)
						self._sig = 0
						return self._sig
				sigs.sort()
				sig = Sig(self.cfg.sig)
				sig.update(''.join(sigs))
				sig = sig.digest()
				if sig != old_sig:
					if __debug__ and is_debug: debug('task: sig changed: ' + str(self))
					# Either the include path or a source or header content has changed.
					# We must recompute the implicit deps.
					self._sig = 0
					return self._sig
				self._sig = sig
				return sig
	else:
		def process(self):
			self.cfg.base_cfg.process(self)
			Task.process(self)

		if True: # faster
			def post_process(self): self.project.task_states[self.uid] = (self.sig, self._implicit_deps)

			@property
			def sig(self):
				try: return self._sig
				except AttributeError:
					sig = Sig(self.cfg.sig)
					sig.update(self.source.sig)
					new_implicit_deps = False
					try: old_sig, self._implicit_deps = self.project.task_states[self.uid]
					except KeyError:
						old_sig = None
						self._implicit_deps, not_found = self.cfg.base_cfg.cpp.scan_deps(self.source, self.cfg.paths)
						if __debug__ and is_debug and len(not_found): debug('cpp: deps not found: ' + self.source.path + ': '+ str([str(x) for x in not_found]))
						new_implicit_deps = True
						sigs = [s.sig for s in self._implicit_deps]
					else:
						try: sigs = [s.sig for s in self._implicit_deps]
						except OSError:
							# A cached implicit dep does not exist anymore.
							# We must recompute the implicit deps.
							self._implicit_deps, not_found = self.cfg.base_cfg.cpp.scan_deps(self.source, self.cfg.paths)
							if __debug__ and is_debug and len(not_found): debug('cpp: deps not found: ' + self.source.path + ': '+ str([str(x) for x in not_found]))
							new_implicit_deps = True
							sigs = [s.sig for s in self._implicit_deps]
					sigs.sort()
					sig.update(''.join(sigs))
					sig = sig.digest()
					if sig != old_sig:
						if __debug__ and is_debug: debug('task: sig changed: ' + self.target.path)
						if not new_implicit_deps:
							# Either the include path or a source or header content has changed.
							# We must recompute the implicit deps.
							sig = Sig(self.cfg.sig)
							sig.update(self.source.sig)
							self._implicit_deps, not_found = self.cfg.base_cfg.cpp.scan_deps(self.source, self.cfg.paths)
							if __debug__ and is_debug and len(not_found): debug('cpp: deps not found: ' + self.source.path + ': '+ str([str(x) for x in not_found]))
							sigs = [s.sig for s in self._implicit_deps]
							sigs.sort()
							sig.update(''.join(sigs))
							sig = sig.digest()
					self._sig = sig
					return sig
		else: # slower
			def post_process(self): self.project.task_states[self.uid] = (self.sig, self._implicit_deps, self._implicit_deps_sig)

			@property
			def sig(self):
				try: return self._sig
				except AttributeError:
					scan_implicit_deps = False
					try: old_sig, self._implicit_deps, self._implicit_deps_sig = self.project.task_states[self.uid]
					except KeyError:
						old_sig = None
						scan_implicit_deps = True
					else:
						try:
							for dep in self._implicit_deps:
								if dep.changed:
									scan_implicit_deps = True
									break
						except OSError:
							# A cached implicit dep does not exist anymore.
							# We must recompute the implicit deps.
							scan_implicit_deps = True
					if scan_implicit_deps: self._do_scan_implicit_deps()
					sig = Sig(self.cfg.sig)
					sig.update(self.source.sig)
					sig.update(self._implicit_deps_sig)
					sig = sig.digest()
					if sig != old_sig:
						if __debug__ and is_debug: debug('task: sig changed: ' + self.target.path)
						if not scan_implicit_deps:
							# Either the include path or the source content has changed.
							# We must recompute the implicit deps.
							self._do_scan_implicit_deps()
							sig = Sig(self.cfg.sig)
							sig.update(self.source.sig)
							sig.update(self._implicit_deps_sig)
							sig = sig.digest()
					self._sig = sig
					return sig

			def _do_scan_implicit_deps(self):
				if __debug__ and is_debug: debug('task: scanning implicit deps: ' + self.source.path)
				self._implicit_deps, not_found = self.cfg.base_cfg.cpp.scan_deps(self.source, self.cfg.paths)
				sigs = [s.sig for s in self._implicit_deps]
				sigs.sort()
				self._implicit_deps_sig = Sig(''.join(sigs)).digest()

class ModTask(Task):
	def __init__(self, mod_cfg, name, aliases = None):
		Task.__init__(self, mod_cfg.project, aliases)
		self.cfg = mod_cfg
		self.name = name
		self.sources = []

	def __str__(self): return str(self.target)

	@property
	def uid(self): return self.target

	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			sig = Sig(self.cfg.sig)
			for t in self.in_tasks: sig.update(t.sig)
			# allow pre-built objects as sources
			ts = [t.target for t in self.in_tasks]
			for s in self.sources:
				if s not in ts: sig.update(s.sig)
			sig = self._sig = sig.digest()
			return sig

	@property
	def target(self):
		try: return self._target
		except AttributeError:
			target = self._target = self.cfg.base_cfg.target(self)
			return target

	def process(self):
		self.cfg.base_cfg.process(self)
		Task.process(self)
		
	@property
	def cxx_cfg(self): return self.cfg.cxx_cfg

	def add_new_cxx_task(self, source):
		t = CxxTask(self.cxx_cfg)
		t.source = source
		t.target = self.target.parent.node_path(source.path[:source.path.rfind('.')] + '.o')
		self.add_in_task(t)
		self.sources.append(t.target)
		return t

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
