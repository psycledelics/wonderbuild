#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2007-2013 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os

from wonderbuild.logger import is_debug, debug
from wonderbuild.option_cfg import OptionCfg
from wonderbuild.task import Persistent, Task

from _build_cfg import BuildCfg

class UserBuildCfgTask(BuildCfg, OptionCfg, Persistent, Task):
	def clone(self, class_ = None):
		if class_ is None: class_ = BuildCfg
		return class_.clone(self, class_)

	# OptionCfg
	signed_os_environ = set(['PATH', 'CXX', 'CXXFLAGS', 'LD', 'LDFLAGS', 'AR', 'RANLIB'])

	# OptionCfg
	signed_options = set([
		'cxx',
		'cxx-flags',
		'ld',
		'ld-flags',
		'ar',
		'ranlib',
		'static',
		'pic-static'
	])

	# OptionCfg(OptionDecl)
	known_options = signed_options | set(['check-missing', 'relink-on-shared-dep-impl-change', 'input-abs-paths'])

	# OptionCfg(OptionDecl)
	@staticmethod
	def generate_option_help(help):
		help['check-missing'] = ('[yes|no]', 'check for missing built files; rebuild files you manually deleted in the build dir', 'yes')

		help['relink-on-shared-dep-impl-change'] = ('[yes|no]',
			'relink clients of a shared lib if its implementation changed; '
			'Normaly when only the implementation changed, and not the interface, clients are not impacted',
			'no')

		help['input-abs-paths'] = ('[yes|no]',
			'use absolute paths for source input files to the compiler. '
			'Using absolute paths may let you click on error lines to open the files.',
			'no => use paths relative to the build dir')

		help['cxx']           = ('<prog>', 'use <prog> as c++ compiler', 'CXX env var: ' + os.environ.get('CXX', '(not set)'))
		help['cxx-flags']     = ('[flags]', 'use specific c++ compiler flags', 'CXXFLAGS env var: ' + os.environ.get('CXXFLAGS', '(not set)'))
		help['ld']            = ('<prog>', 'use <prog> as shared lib and program linker', 'LD env var: ' + os.environ.get('LD', '(not set)'))
		help['ld-flags']      = ('[flags]', 'use specific linker flags', 'LDFLAGS env var: ' + os.environ.get('LDFLAGS', '(not set)'))
		help['ar']            = ('<prog>', 'use <prog> as static lib archiver', 'AR env var: ' + os.environ.get('AR', '(not set, defaults to ar on posix)'))
		help['ranlib']        = ('<prog>', 'use <prog> as static lib archive indexer', 'RANLIB env var: ' + os.environ.get('RANLIB', '(not set, defaults to using the ar s flag on posix)'))
		
		help['static'] = ('<no|libs|full>',
			'no: build dynamic, shared libs and programs\n'
			'libs: build libs as static archives (rather than dynamic, shared libs),\n'
			'full: like libs but also statically link programs (rather than dynamically using shared libs)',
			'no')
		help['pic-static'] = ('[yes|no]',
			'instruct the compiler to emit pic code even for static libs and programs; '
			'shared libs are of course always pic regardless of this option.',
			'no => non-pic for static libs and programs')

		# posix compiler options -O -g -s
		#help['optim']        = ('<0|1|n>', '...', '0')
		#help['debug']        = ('<yes|no>', '...', 'no')
		#help['strip']        = ('<yes|no>', '...', 'no')

	@staticmethod
	def shared(project):
		try: build_cfg_task = project.__cxx_user_build_cfg_task
		except AttributeError: build_cfg_task = project.__cxx_user_build_cfg_task = UserBuildCfgTask(project)
		return build_cfg_task
	
	def __init__(self, project):
		BuildCfg.__init__(self, project)
		OptionCfg.__init__(self, project)
		Persistent.__init__(self, project.persistent, str(self.__class__))
		Task.__init__(self)
	
	# Task
	def __call__(self, sched_ctx):
		o = self.options

		self.check_missing = o.get('check-missing', 'yes') != 'no'
		self.ld_on_shared_dep_impl_change = o.get('relink-on-shared-dep-impl-change', 'no') != 'no'
		self.use_input_abs_paths = o.get('input-abs-paths', 'no') != 'no'
		
		try:
			old_sig, \
			self.cxx_prog, self.cxx_flags, self.pic, \
			self.shared, self.static_prog, self.ld_prog, self.ld_flags, \
			self.ar_prog, self.ranlib_prog = \
				self.persistent
		except KeyError: old_sig = None
		if old_sig != self.options_sig:
			if __debug__ and is_debug: debug('cfg: cxx: user: parsing options')

			self.cxx_prog = o.get('cxx', None) or os.environ.get('CXX', None)
			if 'cxx-flags' in o: self.cxx_flags = o['cxx-flags'].split()
			else:
				e = os.environ.get('CXXFLAGS', None)
				if e is not None: self.cxx_flags = e.split()
				else: self.cxx_flags = []

			static = o.get('static', 'no')
			self.shared = static == 'no'
			self.static_prog = static == 'full'
			
			self.pic = o.get('pic-static', 'no') != 'no' # this is for programs and static libs only
			
			self.ld_prog = o.get('ld', None) or os.environ.get('LD', None)
			if 'ld-flags' in o: self.ld_flags = o['ld-flags'].split()
			else:
				e = os.environ.get('LDFLAGS', None)
				if e is not None: self.ld_flags = e.split()
				else: self.ld_flags = []
			self.ar_prog = o.get('ar', None) or os.environ.get('AR', None)
			self.ranlib_prog = o.get('ranlib', None) or os.environ.get('RANLIB', None)
			
			if self.cxx_prog    is not None: self.print_desc('user-provided-build-cfg-flags: cxx: ' + self.cxx_prog)
			if len(self.cxx_flags) != 0    : self.print_desc('user-provided-build-cfg-flags: cxx flags: ' + str(self.cxx_flags))
			if self.ld_prog     is not None: self.print_desc('user-provided-build-cfg-flags: ld: ' + self.ld_prog)
			if len(self.ld_flags) != 0     : self.print_desc('user-provided-build-cfg-flags: ld flags: ' + str(self.ld_flags))
			if self.ar_prog     is not None: self.print_desc('user-provided-build-cfg-flags: ar: ' + self.ar_prog)
			if self.ranlib_prog is not None: self.print_desc('user-provided-build-cfg-flags: ranlib: ' + self.ranlib_prog)

			self.persistent = \
				self.options_sig, \
				self.cxx_prog, self.cxx_flags, self.pic, \
				self.shared, self.static_prog, self.ld_prog, self.ld_flags, \
				self.ar_prog, self.ranlib_prog

		if True or 'help' not in o: # XXX needs to be done because check tasks need the cfg impl sig
			from detect_impl import DetectImplCheckTask
			detect_impl = DetectImplCheckTask.shared(self)
			for x in sched_ctx.parallel_wait(detect_impl): yield x
