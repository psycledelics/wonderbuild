#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2007-2013 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os
from collections import deque

from wonderbuild.signature import Sig
from wonderbuild.fhs import FHS
from wonderbuild.logger import is_debug, debug

from _dest_platform import DestPlatform
from _pkg_config import PkgConfigTask as _PkgConfigTask

class BuildCfg(object):
	def __init__(self, project):
		self.project = project
		# client cfg
		self.defines = {}
		self.include_paths = deque()
		self.cxx_flags = []
		self.lib_paths = deque()
		self.libs = []
		self.static_libs = []
		self.shared_libs = []
		self.ld_flags = []
		self.pkg_config = []
		self.frameworks = set() # for darwin
		# build cfg
		self.lang = 'c++'
		self.cxx_prog = self.ld_prog = self.ar_prog = self.ranlib_prog = None
		self.pic = self.shared = self.static_prog = None
		self.includes = deque()
		self.pch = None
		self.check_missing = False
		self.ld_on_shared_dep_impl_change = False
		self.fhs = FHS.shared(project)
		self.impl = self.kind = self.version = None
		self.dest_platform = DestPlatform()
		self.use_input_abs_paths = False
		self.shared_checks = project

	def clone(self, class_=None):
		if class_ is None: class_ = self.__class__
		if __debug__ and is_debug: debug('cfg: clone: ' + str(class_))
		c = class_(self.project)
		# client cfg
		c.defines.update(self.defines)
		c.include_paths.extend(self.include_paths)
		c.cxx_flags += self.cxx_flags
		c.lib_paths.extend(self.lib_paths)
		c.libs += self.libs
		c.static_libs += self.static_libs
		c.shared_libs += self.shared_libs
		c.ld_flags += self.ld_flags
		c.pkg_config += self.pkg_config
		c.frameworks |= self.frameworks
		# build cfg
		c.lang = self.lang
		c.cxx_prog = self.cxx_prog
		c.pic = self.pic
		c.pch = self.pch
		c.includes.extend(self.includes)
		c.ld_prog = self.ld_prog
		c.ar_prog = self.ar_prog
		c.ranlib_prog = self.ranlib_prog
		c.shared = self.shared
		c.static_prog = self.static_prog
		c.check_missing = self.check_missing
		c.ld_on_shared_dep_impl_change = self.ld_on_shared_dep_impl_change
		c.fhs = self.fhs
		c.impl = self.impl
		c.kind = self.kind
		c.version = self.version
		c.dest_platform = self.dest_platform.clone() # not sure it's useful to clone
		c.shared_checks = self.shared_checks
		c.use_input_abs_paths = self.use_input_abs_paths
		return c

	@property
	def _common_sig(self):
		try: return self.__common_sig
		except AttributeError:
			sig = Sig(self.impl.common_env_sig)
			e = os.environ.get('PATH', None)
			if e is not None: sig.update(e)
			sig.update(self.lang, self.kind, str(self.version), self.dest_platform.sig)
			if len(self.pkg_config) != 0:
				sig.update(_PkgConfigTask.env_sig())
				# Note: there is no need to sign self.pkg_config itself since this ends up as cxx_flags and ld_flags
			sig.update(*sorted(self.frameworks))
			sig = self.__common_sig = sig.digest()
			return sig
		
	@property
	def cxx_sig(self):
		try: return self._cxx_sig
		except AttributeError:
			sig = Sig(self._common_sig, self.cxx_prog, str(self.pic))
			for k in sorted(self.defines.iterkeys()):
				sig.update(k)
				v = self.defines[k]
				if v is not None: sig.update(str(v))
			sig.update(*(p.abs_path for p in self.include_paths))
			if self.pch is not None: sig.update(self.pch.sig)
			sig.update(*(i.sig for i in self.includes))
			sig.update(*self.cxx_flags)
			sig.update(self.impl.cxx_env_sig)
			sig = self._cxx_sig = sig.digest()
			return sig

	@property
	def _common_mod_sig(self):
		try: return self.__common_mod_sig
		except AttributeError:
			sig = Sig(self._common_sig, str(self.shared), str(self.static_prog))
			sig.update(*(p.abs_path for p in self.lib_paths))
			sig.update(*self.libs)
			sig.update(*self.static_libs)
			sig.update(*self.shared_libs)
			sig.update(self.impl.common_mod_env_sig)
			sig = self.__common_mod_sig = sig.digest()
			return sig

	@property
	def ld_sig(self):
		try: return self._ld_sig
		except AttributeError:
			sig = Sig(self._common_mod_sig)
			sig.update(self.ld_prog)
			for f in self.ld_flags: sig.update(f)
			sig.update(self.impl.ld_env_sig)
			sig = self._ld_sig = sig.digest()
			return sig

	@property
	def ar_ranlib_sig(self):
		try: return self._ar_ranlib_sig
		except AttributeError:
			sig = Sig(self._common_mod_sig)
			sig.update(self.ar_prog)
			if self.ranlib_prog is not None: sig.update(self.ranlib_prog)
			sig.update(self.impl.ar_ranlib_env_sig)
			sig = self._ar_ranlib_sig = sig.digest()
			return sig

	# generic cxx args not tied to a particular PreCompileTask or BatchCompileTask
	@property
	def cxx_args(self):
		try: return self._cxx_args
		except AttributeError:
			args = self._cxx_args = self.impl.cfg_cxx_args(self)
			if __debug__ and is_debug: debug('cfg: cxx: build: cxx: ' + str(args))
			return args

	# generic ld args not tied to a particular ModTask
	@property
	def ld_args(self):
		try: return self._ld_args
		except AttributeError:
			args = self._ld_args = self.impl.cfg_ld_args(self)
			if __debug__ and is_debug: debug('cfg: cxx: build: ld: ' + str(args))
			return args

	# generic ar and ranlib args not tied to a particular ModTask
	@property
	def ar_ranlib_args(self):
		try: return self._ar_ranlib_args
		except AttributeError:
			args = self._ar_ranlib_args = self.impl.cfg_ar_ranlib_args(self)
			if __debug__ and is_debug: debug('cfg: cxx: build: ar ranlib: ' + str(args))
			return args

	# used in cfg.impl for PreCompileTask, BatchCompileTask and ModTask
	def bld_rel_path(self, node):
		path = node.rel_path(self.project.bld_dir)
		if not os.path.isabs(path): path = os.path.join(os.pardir, os.pardir, path)
		return path
	# used in cfg.impl for PreCompileTask, BatchCompileTask and ModTask
	def bld_rel_path_or_abs_path(self, node): return self.use_input_abs_paths and node.abs_path or self.bld_rel_path(node)
	# used in cfg.impl for PreCompileTask, BatchCompileTask and ModTask
	def bld_rel_name_or_abs_path(self, node): return self.use_input_abs_paths and node.abs_path or node.name
