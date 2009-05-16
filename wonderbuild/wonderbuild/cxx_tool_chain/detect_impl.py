#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2007-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from wonderbuild.logger import is_debug, debug, silent
from wonderbuild.subprocess_wrapper import exec_subprocess, exec_subprocess_pipe

def select_impl(user_build_cfg):
	self = user_build_cfg

	if self.kind == 'gcc':
		from gcc_impl import Impl
		self.impl = Impl()
	elif self.kind == 'msvc':
		from msvc_impl import Impl
		self.impl = Impl(self.project.persistent)

def detect_impl(user_build_cfg):
	self = user_build_cfg
	
	o = self.options
	if self.cxx_prog is not None:
		if not silent:
			desc = 'checking for c++ compiler: ' + self.cxx_prog
			self.print_check(desc)
		try: r, out, err = exec_subprocess_pipe([self.cxx_prog, '-dumpversion'], silent = True)
		except Exception, e:
			if __debug__ and is_debug: debug('cfg: ' + desc + ': ' + str(e))
			r = 1
		if r == 0: self.kind = 'gcc'
		else:
			try: r, out, err = exec_subprocess_pipe([self.cxx_prog, '/?'], input = '', silent = True)
			except Exception, e:
				if __debug__ and is_debug: debug('cfg: ' + desc + ': ' + str(e))
				r = 1
			if r == 0: self.kind = 'msvc'
			else: self.kind = None
	else:
		if not silent:
			desc = 'checking for c++ compiler'
			self.print_check(desc)
			self.print_check(desc + ': g++')
		try: r, out, err = exec_subprocess_pipe(['g++', '-dumpversion'], silent = True)
		except Exception, e:
			if __debug__ and is_debug: debug('cfg: ' + desc + ': ' + str(e))
			r = 1
		if r == 0:
			self.kind = 'gcc'
			self.cxx_prog = 'g++'
		else:
			if not silent: self.print_check(desc + ': msvc')
			try: r, out, err = exec_subprocess_pipe(['cl'], silent = True)
			except Exception, e:
				if __debug__ and is_debug: debug('cfg: ' + desc + ': ' + str(e))
				r = 1
			if r == 0:
				self.kind = 'msvc'
				self.cxx_prog = 'cl'
			else: self.kind = None
	if self.kind == 'gcc':
		self.version = out.rstrip('\n')
		from gcc_impl import Impl
		self.impl = Impl()
	elif self.kind == 'msvc':
		self.version = err[:err.find('\n')]
		x = 'Version '
		self.version = self.version[self.version.find(x) + len(x):]
		x = self.version.rfind(' for')
		if x >= 0: self.version = self.version[:x]
		from msvc_impl import Impl
		self.impl = msvc.Impl(self.project.persistent)
	else:
		if not silent: self.print_check_result(desc, 'not found', '31')
		return
	if not silent: self.print_check_result(desc, str(self.kind) + ' version ' + str(self.version), '32')
	cxx_prog, ld_prog, ar_prog, ranlib_prog = self.impl.progs(self)
	if 'cxx' not in o: self.cxx_prog = cxx_prog
	if 'cxx-mod-ld' not in o: self.ld_prog = ld_prog
	if 'cxx-mod-ar' not in o: self.ar_prog = ar_prog
	if 'cxx-mod-ranlib' not in o: self.ranlib_prog = ranlib_prog
