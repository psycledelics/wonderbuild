#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2007-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os, threading
#python 2.5.0a1 from __future__ import with_statement

from options import options, known_options, help
from logger import out, is_debug, debug, colored, silent
from signature import Sig
from cfg import Cfg
from cpp_include_scanner import IncludeScanner
from task import Task, exec_subprocess_pipe

class UserCfg(Cfg):
	_cxx_options = set([
		'--cxx',
		'--cxx-flags',
		'--cxx-debug',
		'--cxx-optim',
		'--cxx-pic'
	])

	_mod_options = set([
		'--cxx-mod-shared',
		'--cxx-mod-ld',
		'--cxx-mod-ld-flags',
		'--cxx-mod-ar',
		'--cxx-mod-ar-flags',
		'--cxx-mod-ranlib',
		'--cxx-mod-ranlib-flags'
	])
	
	_options = _cxx_options | _mod_options

	def help(self):
		help['--cxx-flags']            = ('--cxx-flags=[flags]', 'use specific c++ compiler flags')
		help['--cxx-debug']            = ('--cxx-debug=<yes|no>', 'make the c++ compiler produce debugging information or not', 'no')
		help['--cxx-optim']            = ('--cxx-optim=<level>', 'use c++ compiler optimisation <level>')
		help['--cxx-pic']              = ('--cxx-pic=<yes|no>', 'make the c++ compiler emit pic code rather than non-pic code for static libs and programs (always pic for shared libs)', 'no (for static libs and programs)')
		help['--cxx-mod-shared']       = ('--cxx-mod-shared=<yes|no>', 'build and link shared libs (rather than static libs)', 'yes unless pic is set explicitly to no')
		help['--cxx-mod-ld']           = ('--cxx-mod-ld=<prog>', 'use <prog> as shared lib and program linker')
		help['--cxx-mod-ld-flags']     = ('--cxx-mod-ld-flags=[flags]', 'use specific linker flags')
		help['--cxx-mod-ar']           = ('--cxx-mod-ar=<prog>', 'use <prog> as static lib archiver', 'ar')
		help['--cxx-mod-ar-flags']     = ('--cxx-mod-ar-flags=[flags]', 'use specific archiver flags', 'rc')
		help['--cxx-mod-ranlib']       = ('--cxx-mod-ranlib=<prog>', 'use <prog> as static lib archive indexer', 'ranlib')
		help['--cxx-mod-ranlib-flags'] = ('--cxx-mod-ranlib-flags=[flags]', 'use specific archive indexer flags')
	
	def configure(self):
		try:
			old_sig, \
			self.kind, self.version, \
			self.cxx_prog, self.cxx_flags, self.pic, self.optim, self.debug, \
			self.shared, self.ld_prog, self.ld_flags, \
			self.ar_prog, self.ar_flags, self.ranlib_prog, self.ranlib_flags, \
			self._cxx_args, self._mod_args = \
				self.project.state_and_cache[self.__class__.__name__]
		except KeyError: parse = True
		else: parse = old_sig != self.sig

		if parse:
			if __debug__ and is_debug: debug('cfg: cxx: user: parsing options')
			
			self.shared = self.pic = None
			self.optim = None
			self.debug = False

			cxx_prog = cxx_flags = ld_prog = ld_flags = ar_prog = ar_flags = ranlib_prog = ranlib_flags = False
			for o in options:
				if o.startswith('--cxx='):
					self.cxx_prog = o[len('--cxx='):]
					cxx_prog = True
				elif o.startswith('--cxx-flags='):
					self.cxx_flags = o[len('--cxx-flags='):].split()
					cxx_flags = True
				elif o.startswith('--cxx-pic='): self.pic = o[len('--cxx-pic='):] != 'no'
				elif o.startswith('--cxx-optim='): self.optim = o[len('--cxx-optim='):]
				elif o.startswith('--cxx-debug='): self.debug = o[len('--cxx-debug='):] == 'yes'
				elif o.startswith('--cxx-mod-shared'): self.shared = o[len('--cxx-mod-shared='):] != 'no'
				elif o.startswith('--cxx-mod-ld='):
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

			if self.pic is None:
				if self.shared is None: self.shared = True
				self.pic = False
			elif self.shared is None: self.shared = self.pic
			
			if not cxx_prog: self.cxx_prog = 'c++'

			if not silent: self.print_desc('checking for c++ compiler')
			r, out, err = exec_subprocess_pipe([self.cxx_prog, '-dumpversion'], silent = True)
			if r != 0:
				if not silent: self.print_result_desc('not gcc\n', '31')
				self.kind = None
				self.version = None
			else:
				self.kind = 'gcc'
				self.version = out.rstrip('\n')
				import gcc
				self.impl = gcc.CfgImpl()
				
			if not silent: self.print_result_desc(self.kind + ' version ' + self.version + '\n', '32')

			if not cxx_flags:
				flags = os.environ.get('CXXFLAGS', None)
				if flags is not None: self.cxx_flags = flags.split()
				else: self.cxx_flags = []

			if not ld_prog: self.ld_prog = self.impl.ld_prog
			if not ld_flags:
				flags = os.environ.get('LDFLAGS', None)
				if flags is not None: self.ld_flags = flags.split()
				else: self.ld_flags = []

			if not ar_prog: self.ar_prog = self.impl.ar_prog
			if not ar_flags:
				self.ar_flags = os.environ.get('ARFLAGS', None)
				if self.ar_flags is None:
					if self.kind == 'gcc': self.ar_flags = 'rcus'
					else: self.ar_flags = 'rc'
				
			if not ranlib_prog: self.ranlib_prog = self.impl.ranlib_prog
			if not ranlib_flags: self.ranlib_flags = os.environ.get('RANLIBFLAGS', None)
			
			self.project.state_and_cache[self.__class__.__name__] = \
				self.sig, \
				self.kind, self.version, \
				self.cxx_prog, self.cxx_flags, self.pic, self.optim, self.debug, \
				self.shared, self.ld_prog, self.ld_flags, \
				self.ar_prog, self.ar_flags, self.ranlib_prog, self.ranlib_flags, \
				self.cxx_args, self.mod_args

		elif self.kind == 'gcc':
			import gcc
			self.impl = gcc.CfgImpl()
		else:
			self.cpp = IncludeScanner(self.project.state_and_cache)

		if self.impl is None:
			raise Exception, 'unsupported c++ compiler'

	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			sig = Sig(self.env_sig)
			sig.update(self.options_sig) # TODO don't sign the options, because we miss the defaults
			sig = self._sig = sig.digest()
			return sig

	@property
	def env_sig(self):
		try: return self._env_sig
		except AttributeError:
			sig = Sig()
			e = os.environ.get('PATH', None)
			if e is not None: sig.update(e)
			sig = self._env_sig = sig.digest()
			return sig

	@property
	def cxx_options_sig(self):
		try: return self._cxx_options_sig
		except AttributeError:
			sig = Sig()
			for o in options:
				for oo in self.__class__._cxx_options:
					if o.startswith(oo + '='): sig.update(o)
			sig = self._cxx_options_sig = sig.digest()
			return sig

	@property
	def mod_options_sig(self):
		try: return self._mod_options_sig
		except AttributeError:
			sig = Sig()
			for o in options:
				for oo in self.__class__._mod_options:
					if o.startswith(oo + '='): sig.update(o)
			sig = self._mod_options_sig = sig.digest()
			return sig

	@property
	def cxx_sig(self):
		try: return self._cxx_sig
		except AttributeError:
			sig = Sig(self.cxx_options_sig) # TODO don't sign the options, because we miss the defaults
			sig.update(self.env_sig) # TODO sign abs prog paths instead
			sig.update(self.impl.cxx_env_sig)
			sig = self._cxx_sig = sig.digest()
			return sig

	@property
	def mod_sig(self):
		try: return self._mod_sig
		except AttributeError:
			sig = Sig(self.mod_options_sig) # TODO don't sign the options, because we miss the defaults
			sig.update(self.env_sig) # TODO sign abs prog paths instead
			sig.update(self.impl.mod_env_sig)
			sig = self._mod_sig = sig.digest()
			return sig

	@property
	def cxx_args(self):
		try: return self._cxx_args
		except AttributeError:
			args = self._cxx_args = self.impl.user_cfg_cxx_args(self)
			if __debug__ and is_debug: debug('cfg: cxx: user: cxx: ' + str(args))
			return args

	@property
	def mod_args(self):
		try: return self._mod_args
		except AttributeError:
			args = self._mod_args = self.impl.user_cfg_mod_args(self)
			if __debug__ and is_debug: debug('cfg: cxx: user: mod: ' + str(args))
			return args

class DevCfg(Cfg):
	def __init__(self, user_cfg, kind):
		Cfg.__init__(self, user_cfg.project)
		self.user_cfg = user_cfg
		self.kind = kind

	@property
	def impl(self): return self.user_cfg.impl
	
	def configure(self):
		self.pkgs = []
		self.include_paths = []
		self.defines = {}
		self.pic = self.user_cfg.pic
		if self.kind == 'prog':
			self.shared = False
			self.ld = True
		else:
			self.shared = self.ld = self.user_cfg.shared
			if self.shared and not self.pic:
				debug('cfg: cxx: dev: shared lib => overriding cfg to pic')
				self.pic = True

		self.libs_paths = []
		self.libs = []
		self.static_libs = []
		self.shared_libs = []

	@property
	def cxx_sig(self):
		try: return self._cxx_sig
		except AttributeError:
			sig = Sig(self.user_cfg.cxx_sig)
			sig.update(str(self.pic))
			for k, v in self.defines.iteritems():
				sig.update(k)
				if v is not None: sig.update(v)
			for p in self.include_paths: sig.update(p.path)
			for p in self.pkgs: sig.update(p.sig)
			sig = self._cxx_sig = sig.digest()
			return sig

	@property
	def mod_sig(self):
		try: return self._mod_sig
		except AttributeError:
			sig = Sig(self.user_cfg.mod_sig)
			sig.update(str(self.shared))
			for p in self.libs_paths: sig.update(p.path)
			for l in self.libs: sig.update(l)
			for l in self.static_libs: sig.update(l)
			for l in self.shared_libs: sig.update(l)
			for p in self.pkgs: sig.update(p.sig)
			sig = self._mod_sig = sig.digest()
			return sig

	@property
	def cxx_args(self):
		self.lock.acquire()
		try:
			try: return self._cxx_args
			except AttributeError:
				args = self.user_cfg.cxx_args[:]
				self.impl.dev_cfg_cxx_args(self, args)
				for p in self.pkgs: args += p.cxx_args
				if __debug__ and is_debug: debug('cfg: cxx: dev: cxx: ' + str(args))
				self._cxx_args = args
				return args
		finally: self.lock.release()

	@property
	def mod_args(self):
		self.lock.acquire()
		try:
			try: return self._mod_args
			except AttributeError:
				ld_args, ar_args, ranlib_args = self.user_cfg.mod_args
				if not self.ld:
					args = ar_args, ranlib_args
				else:
					args = ld_args[:]
					self.impl.dev_cfg_ld_args(self, args)
					for p in self.pkgs: args += p.mod_args
				if __debug__ and is_debug: debug('cfg: cxx: dev: mod: ' + str(args))
				self._mod_args = args
				return args
		finally: self.lock.release()

class CxxTask(Task):
	def __init__(self, dev_cfg):
		Task.__init__(self, dev_cfg.project)
		self.cfg = dev_cfg
		self.source = None
		self.target = None

	@property
	def user_cfg(self): return self.cfg.user_cfg
	
	@property
	def impl(self): return self.user_cfg.impl

	def __str__(self): return str(self.target)

	@property
	def uid(self): return self.target

	@property
	def old_sig(self):
		try: return self.project.task_states[self.uid][0]
		except KeyError: return None

	@property
	def sig(self): return self.impl.cxx_task_sig(self)

	def process(self):
		dir = self.target.parent
		lock = dir.lock
		try:
			lock.acquire()
			dir.make_dir()
		finally: lock.release()
		if not silent:
			if self.cfg.pic:
				self.print_desc('compiling pic/shared object from c++ ' +
					self.source.path + ' -> ' + self.target.path, color = '7;1;34')
			else:
				self.print_desc('compiling non-pic/static object from c++ ' +
					self.source.path + ' -> ' + self.target.path, color = '7;34')
		self.impl.process_cxx_task(self)
		Task.process(self)

	def post_process(self): self.impl.post_process_cxx_task(self)

class ModTask(Task):
	def __init__(self, dev_cfg, name, aliases = None):
		Task.__init__(self, dev_cfg.project, aliases)
		self.cfg = dev_cfg
		self.name = name
		self.sources = []

	@property
	def user_cfg(self): return self.cfg.user_cfg
	
	@property
	def impl(self): return self.user_cfg.impl

	def __str__(self): return str(self.target)

	@property
	def uid(self): return self.target

	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			sig = Sig(self.cfg.mod_sig)
			sig.update(self.impl.mod_task_sig(self))
			for t in self.in_tasks: sig.update(t.sig)
			sig = self._sig = sig.digest()
			return sig

	@property
	def target(self):
		try: return self._target
		except AttributeError:
			target = self._target = self.impl.mod_task_target(self)
			return target

	def process(self):
		if not silent:
			if self.cfg.ld:
				if self.cfg.kind == 'prog':
					self.print_desc('linking program ' + self.target.path, color = '7;1;32')
				elif self.cfg.kind == 'loadable':
					self.print_desc('linking loadable module ' + self.target.path, color = '7;1;34')
				else:
					self.print_desc('linking shared lib ' + self.target.path, color = '7;1;33')
			else: self.print_desc('archiving and indexing static lib ' + self.target.path, color = '7;36')
		self.impl.process_mod_task(self)
		Task.process(self)
		
	def add_new_cxx_task(self, source):
		t = CxxTask(self.cfg)
		t.source = source
		t.target = self.target.parent.node_path(source.path[:source.path.rfind('.')] + '.o')
		self.add_in_task(t)
		self.sources.append(t.target)
		return t

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
	def cxx_args(self):
		self.lock.acquire()
		try:
			try: return self._cxx_args
			except AttributeError:
				args = [self.prog, '--cflags'] + self.flags + self.pkgs
				if not silent: self.print_desc('getting pkg-config compile flags: ' + ' '.join(self.pkgs))
				r, out, err = exec_subprocess_pipe(args, silent = True)
				if r != 0: 
					self.print_result_desc('error\n', color = '31')
					raise Exception, r
				self.print_result_desc('ok\n', color = '32')
				out = out.rstrip('\n').split()
				self._cxx_args = out
				return out
		finally: self.lock.release()

	@property
	def mod_args(self, static = False):
		self.lock.acquire()
		try:
			try: return self._mod_args
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
				self._mod_args = out
				return out
		finally: self.lock.release()

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
