#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2007-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os, threading
#python 2.5.0a1 from __future__ import with_statement

from options import options, known_options, help
from logger import out, is_debug, debug, colored, silent
from signature import Sig
from cfg import Cfg
from task import Task, exec_subprocess_pipe

class ClientCxxCfg(object):
	def __init__(self, project):
		self.project = project
		self.include_paths = []
		self.defines = {}
		self.cxx_flags = []
		self.pkgs = []
		
	def apply(self, other):
		for i in other.include_paths: self.include_paths.append(i)
		self.defines.update(other.defines)
		for f in other.cxx_flags: self.cxx_flags.append(f)
		for p in other.pkgs: self.pkgs.append(p)
		
	def clone(self):
		c = self.__class__(self.project)
		c.apply(self)
		return c
		
class BuildCxxCfg(ClientCxxCfg):
	def __init__(self, project)
		ClientCxxCfg.__init__(self, project)
		self.cxx_prog = 'c++'
		self.pic = True
		self.includes = []
		self.impl = None
	
	def apply(self, other):
		ClientCxxCfg.apply(self, other)
		self.cxx_prog = other.cxx_prog
		self.pic = other.pic
		for i in other.includes: self.includes.append(i)
		self.impl = other.impl

	def apply_client(self, other): ClientCxxCfg.apply(self, other)

class ClientLinkCfg(object)
	def __init__(self, project)
		self.project = project
		self.lib_paths = []
		self.libs = []
		self.ld_flags = []
		self.pkgs = []

	def apply(self, other):
		for i in other.lib_paths: self.lib_paths.append(i)
		for l in other.libs: self.libs.append(l)
		for f in other.ld_flags: self.ld_flags.append(f)
		for p in other.pkgs: self.pkgs.append(p)
		
	def clone(self):
		c = self.__class__(self.project)
		c.apply(self)
		return c

class BuildLinkCfg(ClientLinkCfg)
	def __init__(self, project):
		ClientLinkCfg.__init__(self, project)
		self.ld_prog = 'c++'
		self.ar_prog = 'ar'
		self.ranlib_prog = other.ranlib_prog
		self.shared = True

	def apply(self):
		self.ld_prog = other.ld_prog
		self.ar_prog = other.ar_prog
		self.ranlib_prog = other.ranlib_prog
		self.shared = other.shared
		
	def apply_client(self, other): ClientLinkCfg.apply(self, other)

class ClientCfg(object):
	def __init__(self, project)
		self.cxx = ClientCxxCfg(project)
		self.link = ClientLinkCfg(project)
		
	def apply(self, other):
		self.cxx.apply(other.cxx)
		self.link.apply(other.link)

	def clone(self):
		c = self.__class__(project)
		c.apply(self)
		return c

class BuildCfg(object):
	def __init__(self, project):
		self.cxx = BuildCxxCfg(project)
		self.link = BuildLinkCfg(project)
		
	def apply_client(self, other):
		self.cxx.apply_client(other)
		self.link.apply_client(other)

class UserBuildCxxCfg(BuildCxxCfg, Cfg):
	def __init__(self, project):
		BuildCxxCfg.__init__(self, project)
		Cfg.__init__(self, project)
		
	_options = set([
		'--cxx=',
		'--cxx-flags=',
		'--cxx-debug=',
		'--cxx-optim=',
		'--cxx-pic=',
		'--cxx-check-missing='
	])

	def help(self):
		help['--cxx=']                  = ('--cxx=<prog>', 'use <prog> as c++ compiler')
		help['--cxx-flags=']            = ('--cxx-flags=[flags]', 'use specific c++ compiler flags')
		help['--cxx-debug=']            = ('--cxx-debug=<yes|no>', 'make the c++ compiler produce debugging information or not', 'no')
		help['--cxx-optim=']            = ('--cxx-optim=<level>', 'use c++ compiler optimisation <level>')
		help['--cxx-pic=']              = ('--cxx-pic=<yes|no>', 'make the c++ compiler emit pic code rather than non-pic code for static libs and programs (always pic for shared libs)', 'no (for static libs and programs)')
		help['--cxx-check-missing=']    = ('--cxx-check-missing=<yes|no>', 'check for missing built files (rebuilds files you manually deleted in the build dir)', 'no')
	
	def configure(self):
		try:
			old_sig, self.check_missing, \
			self.kind, self.version, \
			self.cxx_prog, self.cxx_flags, self.pic, self.optim, self.debug, \
			self._cxx_args = \
				self.project.state_and_cache[self.__class__.__name__]
		except KeyError: parse = True
		else: parse = old_sig != self.sig

		if parse:
			if __debug__ and is_debug: debug('cfg: cxx: user: parsing options')
			self.optim = None
			self.pic = self.debug = self.check_missing = False
			cxx_prog = cxx_flags = False
			for o in options:
				if o.startswith('--cxx='): self.cxx.cxx_prog = o[len('--cxx='):]; cxx_prog = True
				elif o.startswith('--cxx-flags='): self.cxx.cxx_flags = o[len('--cxx-flags='):].split(); cxx_flags = True
				elif o.startswith('--cxx-pic='): self.cxx.pic = o[len('--cxx-pic='):] != 'no'
				elif o.startswith('--cxx-optim='): self.optim = o[len('--cxx-optim='):]
				elif o.startswith('--cxx-debug='): self.debug = o[len('--cxx-debug='):] == 'yes'
				elif o.startswith('--cxx-check-missing='): self.check_missing = o[len('--cxx-check-missing='):]  == 'yes'

			if not cxx_prog: self.cxx_prog = 'c++'

			self.print_desc('checking for c++ compiler')
			r, out, err = exec_subprocess_pipe([self.cxx.cxx_prog, '-dumpversion'], silent = True)
			if r != 0:
				if not silent: self.print_result_desc('not gcc\n', '31')
				self.kind = None
				self.version = None
			else:
				self.kind = 'gcc'
				self.version = out.rstrip('\n')
				import gcc
				self.impl = gcc.Impl()
			self.print_result_desc(str(self.kind) + ' version ' + str(self.version) + '\n', '32')

			if not cxx_flags:
				flags = os.environ.get('CXXFLAGS', None)
				if flags is not None: self.cxx_flags = flags.split()
				else: self.cxx_flags = []

			self.project.state_and_cache[self.__class__.__name__] = \
				self.sig, self.check_missing, \
				self.kind, self.version, \
				self.cxx_prog, self.cxx_flags, self.pic, self.optim, self.debug, \
				self.cxx_args

		elif self.kind == 'gcc':
			import gcc
			self.impl = gcc.Impl()

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
	def cxx_sig(self):
		try: return self._cxx_sig
		except AttributeError:
			sig = Sig(self.options_sig) # TODO don't sign the options, because we miss the defaults
			sig.update(self.env_sig) # TODO sign abs prog paths instead
			sig.update(self.impl.cxx_env_sig)
			sig = self._cxx_sig = sig.digest()
			return sig

	@property
	def cxx_args(self):
		try: return self._cxx_args
		except AttributeError:
			args = self._cxx_args = self.impl.user_cfg_cxx_args(self)
			if __debug__ and is_debug: debug('cfg: cxx: user: cxx: ' + str(args))
			return args

class UserBuildCfg(BuildLinkCfg, Cfg):
	def __init__(self, project):
		BuildLinkCfg.__init__(self, project
		Cfg.__init__(self, project)
		
	_options = set([
		'--cxx-mod-shared=',
		'--cxx-mod-ld=',
		'--cxx-mod-ld-flags=',
		'--cxx-mod-ar=',
		'--cxx-mod-ranlib=',
		'--cxx-check-missing='
	])
	
	def help(self):
		help['--cxx-mod-shared=']       = ('--cxx-mod-shared=<yes|no>', 'build and link shared libs (rather than static libs)', 'yes unless pic is set explicitly to no')
		help['--cxx-mod-ld=']           = ('--cxx-mod-ld=<prog>', 'use <prog> as shared lib and program linker')
		help['--cxx-mod-ld-flags=']     = ('--cxx-mod-ld-flags=[flags]', 'use specific linker flags')
		help['--cxx-mod-ar=']           = ('--cxx-mod-ar=<prog>', 'use <prog> as static lib archiver', 'ar')
		help['--cxx-mod-ranlib=']       = ('--cxx-mod-ranlib=<prog>', 'use <prog> as static lib archive indexer', 'ranlib (or via ar s flag for gnu ar)')
		help['--cxx-check-missing=']    = ('--cxx-check-missing=<yes|no>', 'check for missing built files (rebuilds files you manually deleted in the build dir)', 'no')
	
	def configure(self):
		try:
			old_sig, self.check_missing, \
			self.kind, self.version, \
			self.shared, self.ld_prog, self.ld_flags, \
			self.ar_prog, self.ar_flags, self.ranlib_prog, self.ranlib_flags, \
			self._mod_args = \
				self.project.state_and_cache[self.__class__.__name__]
		except KeyError: parse = True
		else: parse = old_sig != self.sig

		if parse:
			if __debug__ and is_debug: debug('cfg: cxx: user: parsing options')
			self.shared = True
			self.check_missing = False
			ld_prog = ld_flags = ar_prog = ranlib_prog = False
			for o in options:
				elif o.startswith('--cxx-mod-shared'): self.shared = o[len('--cxx-mod-shared='):] != 'no'
				elif o.startswith('--cxx-mod-ld='): self.ld_prog = o[len('--cxx-mod-ld='):]; ld = True
				elif o.startswith('--cxx-mod-ld-flags='): self.ld_flags = o[len('--cxx-mod-ld-flags='):].split(); ld_flags = True
				elif o.startswith('--cxx-mod-ar='): self.ar_prog = o[len('--cxx-mod-ar='):]; ar_prog = True
				elif o.startswith('--cxx-mod-ranlib='): self.ranlib_prog = o[len('--cxx-mod-ranlib='):]; ranlib_prog = True
				elif o.startswith('--cxx-check-missing='): self.check_missing = o[len('--cxx-check-missing='):]  == 'yes'

			self.print_desc('checking for c++ linker')
			r, out, err = exec_subprocess_pipe([self.ld_prog, '-dumpversion'], silent = True)
			if r != 0:
				if not silent: self.print_result_desc('not gcc\n', '31')
				self.kind = None
				self.version = None
			else:
				self.kind = 'gcc'
				self.version = out.rstrip('\n')
				import gcc
				self.impl = gcc.Impl()
			self.print_result_desc(str(self.kind) + ' version ' + str(self.version) + '\n', '32')

			if not ld_prog: self.ld_prog = self.impl.ld_prog
			if not ld_flags:
				flags = os.environ.get('LDFLAGS', None)
				if flags is not None: self.ld_flags = flags.split()
				else: self.ld_flags = []

			if not ar_prog: self.ar_prog = self.impl.ar_prog
			self.ar_flags = 'rc'
			if self.kind == 'gcc': self.ar_flags += 's'
				
			if not ranlib_prog: self.ranlib_prog = self.impl.ranlib_prog
			self.ranlib_flags = None
			
			self.project.state_and_cache[self.__class__.__name__] = \
				self.sig, self.check_missing, \
				self.kind, self.version, \
				self.shared, self.ld_prog, self.ld_flags, \
				self.ar_prog, self.ar_flags, self.ranlib_prog, self.ranlib_flags, \
				self.mod_args

		elif self.kind == 'gcc':
			import gcc
			self.impl = gcc.Impl()

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
	def mod_sig(self):
		try: return self._mod_sig
		except AttributeError:
			sig = Sig(self.options_sig) # TODO don't sign the options, because we miss the defaults
			sig.update(self.env_sig) # TODO sign abs prog paths instead
			sig.update(self.impl.mod_env_sig)
			sig = self._mod_sig = sig.digest()
			return sig

	@property
	def mod_args(self):
		try: return self._mod_args
		except AttributeError:
			args = self._mod_args = self.impl.user_cfg_mod_args(self)
			if __debug__ and is_debug: debug('cfg: cxx: user: mod: ' + str(args))
			return args

class UserBuildCfg(Cfg):
	def __init__(self, project):
		Cfg.__init__(self, project)
		self._build_cfg = BuildCfg(project)
		
	@property
	def cxx(self): return self._build_cfg.cxx
	
	@property
	def link(self): return self._build_cfg.link
	
	_cxx_options = set([
		'--cxx=',
		'--cxx-flags=',
		'--cxx-debug=',
		'--cxx-optim=',
		'--cxx-pic='
	])

	_mod_options = set([
		'--cxx-mod-shared=',
		'--cxx-mod-ld=',
		'--cxx-mod-ld-flags=',
		'--cxx-mod-ar=',
		'--cxx-mod-ranlib='
	])
	
	_options = _cxx_options | _mod_options | set([
		'--cxx-check-missing='
	])
	
	def help(self):
		help['--cxx=']                  = ('--cxx=<prog>', 'use <prog> as c++ compiler')
		help['--cxx-flags=']            = ('--cxx-flags=[flags]', 'use specific c++ compiler flags')
		help['--cxx-debug=']            = ('--cxx-debug=<yes|no>', 'make the c++ compiler produce debugging information or not', 'no')
		help['--cxx-optim=']            = ('--cxx-optim=<level>', 'use c++ compiler optimisation <level>')
		help['--cxx-pic=']              = ('--cxx-pic=<yes|no>', 'make the c++ compiler emit pic code rather than non-pic code for static libs and programs (always pic for shared libs)', 'no (for static libs and programs)')
		help['--cxx-mod-shared=']       = ('--cxx-mod-shared=<yes|no>', 'build and link shared libs (rather than static libs)', 'yes unless pic is set explicitly to no')
		help['--cxx-mod-ld=']           = ('--cxx-mod-ld=<prog>', 'use <prog> as shared lib and program linker')
		help['--cxx-mod-ld-flags=']     = ('--cxx-mod-ld-flags=[flags]', 'use specific linker flags')
		help['--cxx-mod-ar=']           = ('--cxx-mod-ar=<prog>', 'use <prog> as static lib archiver', 'ar')
		help['--cxx-mod-ranlib=']       = ('--cxx-mod-ranlib=<prog>', 'use <prog> as static lib archive indexer', 'ranlib (or via ar s flag for gnu ar)')
		help['--cxx-check-missing=']    = ('--cxx-check-missing=<yes|no>', 'check for missing built files (rebuilds files you manually deleted in the build dir)', 'no')
	
	def configure(self):
		try:
			old_sig, self.check_missing, \
			self.kind, self.version, \
			self.cxx.cxx_prog, self.cxx.cxx_flags, self.cxx.pic, self.optim, self.debug, \
			self.link.shared, self.link.ld_prog, self.link.ld_flags, \
			self.link.ar_prog, self.link.ar_flags, self.link.ranlib_prog, self.link.ranlib_flags, \
			self.cxx._cxx_args, self.link._mod_args = \
				self.project.state_and_cache[self.__class__.__name__]
		except KeyError: parse = True
		else: parse = old_sig != self.sig

		if parse:
			if __debug__ and is_debug: debug('cfg: cxx: user: parsing options')
			self.link.shared = self.cxx.pic = self.optim = None
			self.debug = self.check_missing = False
			cxx_prog = cxx_flags = ld_prog = ld_flags = ar_prog = ranlib_prog = False
			for o in options:
				if o.startswith('--cxx='): self.cxx.cxx_prog = o[len('--cxx='):]; cxx_prog = True
				elif o.startswith('--cxx-flags='): self.cxx.cxx_flags = o[len('--cxx-flags='):].split(); cxx_flags = True
				elif o.startswith('--cxx-pic='): self.cxx.pic = o[len('--cxx-pic='):] != 'no'
				elif o.startswith('--cxx-optim='): self.optim = o[len('--cxx-optim='):]
				elif o.startswith('--cxx-debug='): self.debug = o[len('--cxx-debug='):] == 'yes'
				elif o.startswith('--cxx-mod-shared'): self.link.shared = o[len('--cxx-mod-shared='):] != 'no'
				elif o.startswith('--cxx-mod-ld='): self.link.ld_prog = o[len('--cxx-mod-ld='):]; ld = True
				elif o.startswith('--cxx-mod-ld-flags='): self.link.ld_flags = o[len('--cxx-mod-ld-flags='):].split(); ld_flags = True
				elif o.startswith('--cxx-mod-ar='): self.link.ar_prog = o[len('--cxx-mod-ar='):]; ar_prog = True
				elif o.startswith('--cxx-mod-ranlib='): self.link.ranlib_prog = o[len('--cxx-mod-ranlib='):]; ranlib_prog = True
				elif o.startswith('--cxx-check-missing='): self.check_missing = o[len('--cxx-check-missing='):]  == 'yes'
			if self.cxx.pic is None:
				if self.link.shared is None: self.link.shared = True
				self.cxx.pic = False
			elif self.link.shared is None: self.link.shared = self.cxx.pic

			if not cxx_prog: self.cxx.cxx_prog = 'c++'

			self.print_desc('checking for c++ compiler')
			r, out, err = exec_subprocess_pipe([self.cxx.cxx_prog, '-dumpversion'], silent = True)
			if r != 0:
				if not silent: self.print_result_desc('not gcc\n', '31')
				self.kind = None
				self.version = None
			else:
				self.kind = 'gcc'
				self.version = out.rstrip('\n')
				self.link.ld_prog = self.cxx.cxx_prog
				ld_prog = True
				import gcc
				self.impl = gcc.Impl()
			self.print_result_desc(str(self.kind) + ' version ' + str(self.version) + '\n', '32')

			if not cxx_flags:
				flags = os.environ.get('CXXFLAGS', None)
				if flags is not None: self.cxx.cxx_flags = flags.split()
				else: self.cxx.cxx_flags = []

			if not ld_prog: self.link.ld_prog = self.impl.ld_prog
			if not ld_flags:
				flags = os.environ.get('LDFLAGS', None)
				if flags is not None: self.link.ld_flags = flags.split()
				else: self.link.ld_flags = []

			if not ar_prog: self.link.ar_prog = self.impl.ar_prog
			self.link.ar_flags = 'rc'
			if self.kind == 'gcc': self.link.ar_flags += 's'
				
			if not ranlib_prog: self.link.ranlib_prog = self.impl.ranlib_prog
			self.link.ranlib_flags = None
			
			self.project.state_and_cache[self.__class__.__name__] = \
				self.sig, self.check_missing, \
				self.kind, self.version, \
				self.cxx.cxx_prog, self.cxx.cxx_flags, self.cxx.pic, self.optim, self.debug, \
				self.link.shared, self.link.ld_prog, self.link.ld_flags, \
				self.link.ar_prog, self.link.ar_flags, self.link.ranlib_prog, self.link.ranlib_flags, \
				self.cxx.cxx_args, self.link.mod_args

		elif self.kind == 'gcc':
			import gcc
			self.impl = gcc.Impl()

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

class BuildCheck(object):
	def __init__(self, name, base_build_cfg)
		self.name = name
		self._base_build_cfg

	def apply_to(self, build_cfg): pass

	@property
	def source(self): pass

	@property
	def build_cfg(self):
		try: return self._build_cfg
		except AttributeError:
			self._build_cfg = self._base_build_cfg.clone()
			self.apply_to(self._build_cfg)
			return self._build_cfg
		
	@property
	def project(self): return self.base_build_cfg.project
	
	@property
	def uid(self): return self.name
	
	@property
	def result(self):
		try: return self._result
		except AttributeError:
			n = self.project.bld_node.node_path('checks').node_path(self.name)
			changed = False
			if not n.exists: changed = True
			try: old_sig = self.project.state_and_cache[self.uid]
			except KeyError: changed = True
			else:
				sig = Sig(self.source)
				sig.update(self.build.sig)
				sig = sig.digest()
				if old_sig != sig: changed = True
			if changed:
				n.make_dir()
				n = n.node_path('source.cpp')
				f = open(n.path, 'w')
				try: f.write(self.source)
				finally: f.close()
				self._result = self.build_cfg.cxx.impl.process_cxx() == 0
				return self._result
				
class CxxPreCompileTask(Task):
	def __init__(self, build_cxx_cfg, header):
		Task.__init__(self, build_cxx_cfg.project)
		self.cfg = build_cxx_cfg

	@property
	def header(self): pass

	def apply_to_(self, cxx_build_cfg): cxx_build_cfg.includes.append(self.header)

	@property
	def impl(self): return self.cfg.impl

	def __str__(self): return str(header)

	@property
	def uid(self): return self.header #XXX

	@property
	def target_dir(self):
		try: return self._target_dir
		except AttributeError:
			self._target_dir = self.project.bld_node.\
				node_path('precompiled-headers').\
				node_path(self.header.rel_path(self.project.src_node)) #XXX
			return self._target_dir

	def need_process(self):
		changed = False
		try: old_cfg_sig, deps, old_dep_sig = self.project.task_states[self.uid]
		except KeyError:
			if __debug__ and is_debug: debug('task: no state: ' + str(self))
			self.project.task_states[self.uid] = None, None, None
			changed = True
		else:
			if old_cfg_sig != self.cfg.sig:
				if __debug__ and is_debug: debug('task: cxx sig changed: ' + str(self))
				changed = True
			else:
				try: dep_sigs = [dep.sig for dep in deps]
				except OSError:
					# A cached implicit dep does not exist anymore.
					if __debug__ and is_debug: debug('cpp: deps not found: ' + str(self.header))
					changed = True
					break
				dep_sigs.sort()
				dep_sig = Sig(''.join(dep_sigs)).digest()
				if old_dep_sig != sig:
					# The cached implicit deps changed.
					if __debug__ and is_debug: debug('cpp: deps changed: ' + str(self.header))
					changed = True
					break
				if __debug__ and is_debug: debug('task: skip: no change: ' + str(self.header))
		return changed
