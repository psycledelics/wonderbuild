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
from wonderbuild.cxx_tool_chain import PreCompileTasks

class Wonderbuild(ScriptTask):
	@property
	def top_src_dir(self): return self.src_dir.parent.parent

	@property
	def cfg(self): return self._cfg

	@property
	def pch(self):
		try: return self._pch
		except AttributeError:
			self._pch = Wonderbuild.Pch(self.top_src_dir, self.cfg)
			return self._pch

	def __call__(self, sched_ctx):
		from wonderbuild.cxx_tool_chain import UserBuildCfgTask
		cfg = UserBuildCfgTask.shared(self.project)
		for x in sched_ctx.parallel_wait(cfg): yield x
		self._cfg = cfg = cfg.clone()

		if cfg.kind == 'msvc':
			#cfg.defines['WINVER'] = '0x501' # select win xp explicitly because msvc 2008 defaults to vista
			cfg.defines['BOOST_ALL_DYN_LINK'] = None # choose to link against boost dlls
			cfg.cxx_flags += ['-EHa', '-MD'] # basic compilation flags required

		cfg.defines['UNIVERSALIS__META__PACKAGE__NAME'] = '"psycle"'
		cfg.defines['UNIVERSALIS__META__PACKAGE__VERSION'] = 1

	class Pch(PreCompileTasks):
		def __init__(self, top_src_dir, base_cfg):
			PreCompileTasks.__init__(self, 'common-pch', base_cfg)
			self.top_src_dir = top_src_dir

		def __call__(self, sched_ctx):
			from wonderbuild.cxx_tool_chain import PkgConfigCheckTask
			from wonderbuild.std_checks.std_math import StdMathCheckTask
			from wonderbuild.std_checks.dlfcn import DlfcnCheckTask
			from wonderbuild.std_checks.pthread import PThreadCheckTask
			from wonderbuild.std_checks.boost import BoostCheckTask

			check_cfg = self.cfg.clone()
			glibmm = PkgConfigCheckTask.shared(check_cfg, ['glibmm-2.4', 'gmodule-2.0', 'gthread-2.0'])
			self._std_math = std_math = StdMathCheckTask.shared(check_cfg)
			dlfcn = DlfcnCheckTask.shared(check_cfg)
			pthread = PThreadCheckTask.shared(check_cfg)
			self._boost = boost = BoostCheckTask.shared(check_cfg, (1, 34, 1), ('signals', 'thread', 'filesystem', 'date_time'))

			opt = [dlfcn, pthread, glibmm, std_math, boost]
			for x in sched_ctx.parallel_wait(*opt): yield x
			self.public_deps = [x for x in opt if x]
			self.result = True
			for x in PreCompileTasks.__call__(self, sched_ctx): yield x

		def do_cxx_phase(self): self.cfg.include_paths.append(self.top_src_dir / 'build-systems' / 'src')

		@property
		def source_text(self):
			try: return self._source_text
			except AttributeError:
				s = '#include <forced-include.private.hpp>'
				if self._boost: s += '\n#include <pre-compiled/boost.private.hpp>'
				if self._std_math: s += '\n#include <cmath>'
				self._source_text = s
				return s
