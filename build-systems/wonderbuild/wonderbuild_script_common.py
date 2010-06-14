#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2009-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>


##############################################################################
#
# This script is shared by all projects in the trunk.
# It sets some common compiler/linker flags
# and builds some pre-compiled headers to be used by all projects.
#
##############################################################################



from wonderbuild.script import ScriptTask, ScriptLoaderTask

class Wonderbuild(ScriptTask):
	@property
	def cfg(self): return self._cfg

	@property
	def pch(self):
		try: return self._pch
		except AttributeError:
			self._pch = Pch()
			return self._pch

	def __call__(self, sched_ctx):
		project = self.project
		top_src_dir = self.src_dir.parent.parent
		
		from wonderbuild.cxx_tool_chain import UserBuildCfgTask, PkgConfigCheckTask
		from wonderbuild.std_checks.std_math import StdMathCheckTask
		from wonderbuild.std_checks.dlfcn import DlfcnCheckTask
		from wonderbuild.std_checks.pthread import PThreadCheckTask
		from wonderbuild.std_checks.boost import BoostCheckTask
		
		cfg = UserBuildCfgTask.shared(project)
		for x in sched_ctx.parallel_wait(cfg): yield x
		self._cfg = cfg = cfg.clone()

		if cfg.kind == 'msvc': # XXX flags are a mess with msvc
			#cfg.defines['WINVER'] = '0x501' # select win xp explicitly because msvc 2008 defaults to vista
			cfg.defines['BOOST_ALL_DYN_LINK'] = None # choose to link against boost dlls
			cfg.cxx_flags += ['-EHa', '-MD'] # basic compilation flags required

		check_cfg = cfg.clone()
		glibmm = PkgConfigCheckTask.shared(check_cfg, ['glibmm-2.4', 'gmodule-2.0', 'gthread-2.0'])
		std_math = StdMathCheckTask.shared(check_cfg)
		dlfcn = DlfcnCheckTask.shared(check_cfg)
		pthread = PThreadCheckTask.shared(check_cfg)
		boost = BoostCheckTask.shared(check_cfg, (1, 34, 1), ('signals', 'thread', 'filesystem', 'date_time'))

		cfg.defines['UNIVERSALIS__META__PACKAGE__NAME'] = '"psycle"'
		cfg.defines['UNIVERSALIS__META__PACKAGE__VERSION'] = 1

from wonderbuild.cxx_tool_chain import PreCompileTasks

class Pch(PreCompileTasks):
	def __init__(self): PreCompileTasks.__init__(self, 'common-pch', cfg)

	def __call__(self, sched_ctx):
		self.public_deps = [diversalis]
		req = self.public_deps
		opt = [dlfcn, pthread, glibmm, std_math, boost]
		for x in sched_ctx.parallel_wait(*(req + opt)): yield x
		self.result = min(bool(r) for r in req)
		self.public_deps += [x for x in opt if x]
		for x in PreCompileTasks.__call__(self, sched_ctx): yield x
	
	def do_cxx_phase(self): self.cfg.include_paths.append(top_src_dir / 'build-systems' / 'src')

	@property
	def source_text(self):
		try: return self._source_text
		except AttributeError:
			s = '#include <forced-include.private.hpp>'
			if boost: s += '\n#include <pre-compiled/boost.private.hpp>'
			if std_math: s += '\n#include <cmath>'
			self._source_text = s
			return s
