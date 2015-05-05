#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2007-2013 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os

from wonderbuild.logger import is_debug, debug
from wonderbuild.signature import Sig
from wonderbuild.check_task import CheckTask, ok_color
from wonderbuild.subprocess_wrapper import exec_subprocess, exec_subprocess_pipe

from _mod_dep_phases import ModDepPhases

class _PkgConfigTask(CheckTask):

	@staticmethod
	def _shared_uid(class_, pkgs):
		pkgs.sort()
		return str(class_) + ' ' + ' '.join(pkgs)

	def __init__(self, persistent, uid, cfg, pkgs):
		CheckTask.__init__(self, persistent, uid, cfg.shared_checks)
		self.pkgs = pkgs

	@property
	def prog(self): return 'pkg-config'

	def __str__(self): return 'check ' + self.desc

	# CheckTask
	@property
	def desc(self):
		try: return self._desc
		except AttributeError:
			self._desc = self.prog + ' ' + self.what_desc + ' ' + ' '.join(self.pkgs)
			return self._desc

	@property
	def what_desc(self): raise Exception, str(self.__class__) + ' did not redefine the property.'
	
	@property
	def what_args(self): raise Exception, str(self.__class__) + ' did not redefine the property.'

	@property
	def args(self): return [self.prog] + self.pkgs + self.what_args

	# CheckTask
	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			sig = self._sig = _PkgConfigTask.env_sig()
			return sig

	@staticmethod
	def env_sig():
		sig = Sig()
		for name in ('PKG_CONFIG_PATH', 'PKG_CONFIG_LIBDIR', 'PKG_CONFIG_DISABLE_UNINSTALLED'): # PKG_CONFIG_TOP_BUILD_DIR, PKG_CONFIG_ALLOW_SYSTEM_CFLAGS, PKG_CONFIG_ALLOW_SYSTEM_LIBS
			e = os.environ.get(name, None)
			if e is not None: sig.update(e)
		return sig.digest()

# export because _PkgConfigTask.env_sig() is used by BuildCfg._common_sig()
PkgConfigTask = _PkgConfigTask

class _PkgConfigFlagsTask(_PkgConfigTask):

	def __init__(self, persistent, uid, cfg): _PkgConfigTask.__init__(self, persistent, uid, cfg, cfg.pkg_config)

	# _PkgConfigTask(CheckTask)
	def do_check_and_set_result(self, sched_ctx):
		if False: yield
		r, out, err = exec_subprocess_pipe(self.args, silent=True)
		if r != 0: raise Exception, r # Simply short-circuited here because we've already validated the packages with PkgConfigCheckTask.
		self.result = out.split()

	# _PkgConfigTask(CheckTask)
	@property
	def result_display(self):
		if __debug__ and is_debug: return ' '.join(self.result), ok_color
		else: return 'ok', ok_color

	def apply_to(self): raise Exception, str(self.__class__) + ' did not redefine the method.'

class _PkgConfigCxxFlagsTask(_PkgConfigFlagsTask):

	# _PkgConfigFlagsTask(_PkgConfigTask(CheckTask(SharedTask)))
	@classmethod
	def shared_uid(class_, cfg): return _PkgConfigFlagsTask._shared_uid(class_, cfg.pkg_config)

	# _PkgConfigFlagsTask(_PkgConfigTask(CheckTask(SharedTask)))
	@classmethod
	def shared(class_, cfg): return _PkgConfigFlagsTask._shared(class_, cfg.shared_checks, cfg)

	# _PkgConfigFlagsTask(_PkgConfigTask)
	@property
	def what_desc(self): return 'cxx flags'
	
	# _PkgConfigFlagsTask(_PkgConfigTask)
	@property
	def what_args(self): return ['--cflags']

	# _PkgConfigFlagsTask
	def apply_to(self, cfg): cfg.cxx_flags += self.result

# export because _PkgConfigCxxFlagsTask.shared is used by ModTask._mod_phase_callback and _PreCompileTask._cxx_phase_callback
PkgConfigCxxFlagsTask = _PkgConfigCxxFlagsTask

class _PkgConfigLdFlagsTask(_PkgConfigFlagsTask):

	# _PkgConfigFlagsTask(_PkgConfigTask(CheckTask(SharedTask)))
	@classmethod
	def shared_uid(class_, cfg, expose_private_deep_deps):
		uid = _PkgConfigFlagsTask._shared_uid(class_, cfg.pkg_config)
		if expose_private_deep_deps: uid += ' --static'
		return uid

	# _PkgConfigFlagsTask(_PkgConfigTask(CheckTask(SharedTask)))
	@classmethod
	def shared(class_, cfg, expose_private_deep_deps):
		return _PkgConfigFlagsTask._shared(class_, cfg.shared_checks, cfg, expose_private_deep_deps)

	def __init__(self, persistent, uid, cfg, expose_private_deep_deps):
		_PkgConfigFlagsTask.__init__(self, persistent, uid, cfg)
		self.expose_private_deep_deps = expose_private_deep_deps

	# _PkgConfigFlagsTask(_PkgConfigTask)
	@property
	def what_desc(self):
		if self.expose_private_deep_deps: return 'static ld flags'
		else: return 'shared ld flags'
	
	# _PkgConfigFlagsTask(_PkgConfigTask)
	@property
	def what_args(self):
		if self.expose_private_deep_deps: return ['--libs', '--static']
		else: return ['--libs']

	# _PkgConfigFlagsTask
	def apply_to(self, cfg): cfg.ld_flags += self.result

# export because _PkgConfigLdFlagsTask.shared is used by ModTask._mod_phase_callback
PkgConfigLdFlagsTask = _PkgConfigLdFlagsTask

class PkgConfigCheckTask(ModDepPhases, _PkgConfigTask):

	# _PkgConfigTask(CheckTask(SharedTask))
	@classmethod
	def shared_uid(class_, cfg, pkgs): return _PkgConfigTask._shared_uid(class_, pkgs)

	# _PkgConfigTask(CheckTask(SharedTask))
	@classmethod
	def shared(class_, cfg, pkgs): return _PkgConfigTask._shared(class_, cfg.shared_checks, cfg, pkgs)

	def __init__(self, persistent, uid, cfg, pkgs):
		ModDepPhases.__init__(self)
		_PkgConfigTask.__init__(self, persistent, uid, cfg, pkgs)

	# ModDepPhases
	def apply_cxx_to(self, cfg): cfg.pkg_config += self.pkgs
		
	# _PkgConfigTask
	@property
	def what_desc(self): return 'existence'
	
	# _PkgConfigTask
	@property
	def what_args(self): return ['--exists']

	# ModDepPhases(DepTask(Task)), CheckTask(DepTask(Task), SharedTask(Task))
	def __call__(self, sched_ctx):
		for x in ModDepPhases.__call__(self, sched_ctx): yield x
		for x in CheckTask.__call__(self, sched_ctx): yield x

	# _PkgConfigTask(CheckTask)
	def do_check_and_set_result(self, sched_ctx):
		if False: yield
		try: r = exec_subprocess(self.args)
		except Exception, e:
			if __debug__ and is_debug: debug('cfg: ' + self.desc + ': exception: ' + str(e))
			r = 1
		# note: in case of a positive result, we could as well store a positive result for each individual packages
		self.result = r == 0
