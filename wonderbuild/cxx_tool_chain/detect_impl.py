#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2007-2013 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from wonderbuild import UserReadableException
from wonderbuild.logger import colored, is_debug, debug, silent
from wonderbuild.subprocess_wrapper import exec_subprocess, exec_subprocess_pipe
from wonderbuild.check_task import CheckTask, ok_color, failed_color
from wonderbuild.std_checks import ValidCfgCheckTask, ClangCheckTask, DestPlatformCheckTask, PicFlagDefinesPicCheckTask

class DetectImplCheckTask(CheckTask):

	# CheckTask(SharedTask)
	@staticmethod
	def shared_uid(*args, **kw): return 'c++-tool-chain'

	# CheckTask(SharedTask)
	@classmethod
	def shared(class_, user_build_cfg): return CheckTask._shared(class_, user_build_cfg.shared_checks, user_build_cfg)

	def __init__(self, persistent, uid, user_build_cfg):
		CheckTask.__init__(self, persistent, uid, user_build_cfg.shared_checks)
		self.user_build_cfg = user_build_cfg

	# CheckTask
	@property
	def sig(self): return self.user_build_cfg.options_sig

	# CheckTask
	@property
	def result_display(self):
		if not self: return 'not found', failed_color
		else: return str(self.kind) + ' version ' + '.'.join(str(v) for v in self.version), ok_color

	def __bool__(self): return self.kind is not None
	
	@property
	def kind(self): return self.result[0]
	
	@property
	def version(self): return self.result[1]
	
	# CheckTask(DepTask(Task), SharedTask(Task))
	def __call__(self, sched_ctx):
		# Don't do it all directly in do_check_and_set_result because it's not executed when sig hasn't changed.
		for x in CheckTask.__call__(self, sched_ctx): yield x
		cfg = self.user_build_cfg
		cfg.kind = self.kind
		cfg.version = self.version
		if cfg.impl is None: self._select_impl()
		if cfg.impl is None: raise UserReadableException, str(self) + ': no supported c++ compiler found'

		# set the programs
		cxx_prog, ld_prog, ar_prog, ranlib_prog = cfg.impl.progs(cfg)
		if __debug__ and is_debug:
			debug('cfg: ' + self.desc + ': cxx: ' + cxx_prog)
			debug('cfg: ' + self.desc + ': ld: ' + ld_prog)
			debug('cfg: ' + self.desc + ': ar: ' + ar_prog)
			debug('cfg: ' + self.desc + ': ranlib: ' + ranlib_prog)
		if cfg.cxx_prog is None: cfg.cxx_prog = cxx_prog
		if cfg.ld_prog is None: cfg.ld_prog = ld_prog
		if cfg.ar_prog is None: cfg.ar_prog = ar_prog
		if cfg.ranlib_prog is None: cfg.ranlib_prog = ranlib_prog
		
		valid_cfg = ValidCfgCheckTask.shared(cfg)
		clang = ClangCheckTask.shared(cfg)
		dest_platform = DestPlatformCheckTask.shared(cfg)
		pic = PicFlagDefinesPicCheckTask.shared(cfg)
		cfg.dest_platform.pic_flag_defines_pic = True # allows it to be reentrant during the check itself
		for x in sched_ctx.parallel_wait(pic, dest_platform, clang, valid_cfg): yield x
		cfg.dest_platform.bin_fmt = dest_platform.bin_fmt
		cfg.dest_platform.os = dest_platform.os
		cfg.dest_platform.arch = dest_platform.arch
		cfg.dest_platform.pic_flag_defines_pic = bool(pic)
		cfg.impl.kind_is_clang = bool(clang)
	
	# CheckTask
	def do_check_and_set_result(self, sched_ctx):
		if False: yield
		sched_ctx.lock.release()
		try:
			cfg = self.user_build_cfg
			# determine the kind of compiler
			if cfg.cxx_prog is not None: # check the compiler specified in cfg.cxx_prog
				if not silent:
					desc = self.desc + ' ... ' + cfg.cxx_prog
					self.print_check(desc)
				try: r, out, err = exec_subprocess_pipe([cfg.cxx_prog, '-dumpversion'], silent=True) # TODO clang has its own version
				except Exception, e:
					if __debug__ and is_debug: debug('cfg: ' + desc + ': ' + str(e))
					r = 1
				if r == 0: cfg.kind = 'gcc'
				else:
					try: r, out, err = exec_subprocess_pipe([cfg.cxx_prog, '/?'], input = '', silent=True)
					except Exception, e:
						if __debug__ and is_debug: debug('cfg: ' + desc + ': ' + str(e))
						r = 1
					if r == 0: cfg.kind = 'msvc'
					else: cfg.kind = None
			else: # try some compiler program names until we found one available
				if not silent:
					desc = self.desc + ' ...'
					self.print_check(desc + ' g++')
				try: r, out, err = exec_subprocess_pipe(['g++', '-dumpversion'], silent=True)
				except Exception, e:
					if __debug__ and is_debug: debug('cfg: ' + desc + ': ' + str(e))
					r = 1
				if r == 0: cfg.kind = 'gcc'
				else:
					if not silent: self.print_check(desc + ' clang++')
					try: r, out, err = exec_subprocess_pipe(['clang++', '-dumpversion'], silent=True)
					except Exception, e:
						if __debug__ and is_debug: debug('cfg: ' + desc + ': ' + str(e))
						r = 1
					if r == 0: cfg.kind = 'gcc' # TODO actually clang
					else:
						if not silent: self.print_check(desc + ' msvc')
						try: r, out, err = exec_subprocess_pipe(['cl'], silent=True)
						except Exception, e:
							if __debug__ and is_debug: debug('cfg: ' + desc + ': ' + str(e))
							r = 1
						if r == 0: cfg.kind = 'msvc'
						elif False: # pure posix support not tested
							if not silent: self.print_check(desc + ' c++')
							try: r, out, err = exec_subprocess_pipe(['c++'], silent=True)
							except Exception, e:
								if __debug__ and is_debug: debug('cfg: ' + desc + ': ' + str(e))
								r = 1
							if r == 0: cfg.kind = 'posix'
						else: cfg.kind = None
			# set the impl corresponding to the kind
			self._select_impl()
			# read the version
			cfg.version = cfg.impl is not None and cfg.impl.parse_version(out, err) or None
		finally: sched_ctx.lock.acquire()
		
		self.result = cfg.kind, cfg.version

	def _select_impl(self):
		cfg = self.user_build_cfg
		# set the impl corresponding to the kind
		if cfg.kind == 'gcc':
			from gcc_impl import Impl
			cfg.impl = Impl()
		elif cfg.kind == 'msvc':
			from msvc_impl import Impl
			cfg.impl = Impl(self.project.persistent)
		elif cfg.kind == 'posix':
			from posix_impl import Impl
			cfg.impl = Impl(self.project.persistent)
		else: cfg.impl = None
