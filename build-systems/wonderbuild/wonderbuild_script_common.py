#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2009-2011 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>


##############################################################################
#
# This script is shared by all projects in the trunk.
# It sets some common compiler/linker flags
# and builds some pre-compiled headers to be used by all projects.
#
##############################################################################



from wonderbuild.script import ScriptTask, ScriptLoaderTask
from wonderbuild.cxx_tool_chain import UserBuildCfgTask, PreCompileTasks

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
		cfg = UserBuildCfgTask.shared(self.project)
		for x in sched_ctx.parallel_wait(cfg): yield x
		self._cfg = cfg = cfg.clone()

		if cfg.kind == 'msvc': cfg.cxx_flags.append('-EHa') # Asynchronous exception handling is useful for the host to be able to catch plugin crashes.

		cfg.defines['UNIVERSALIS__META__PACKAGE__NAME'] = '"psycle"'
		cfg.defines['UNIVERSALIS__META__PACKAGE__VERSION'] = 1

	class Pch(PreCompileTasks):
		def __init__(self, top_src_dir, base_cfg):
			PreCompileTasks.__init__(self, 'common-pch', base_cfg)
			self.top_src_dir = top_src_dir

		def __call__(self, sched_ctx):
			from wonderbuild.cxx_tool_chain import PkgConfigCheckTask
			from wonderbuild.std_checks.std_math import StdMathCheckTask
			from wonderbuild.std_checks.std_cxx0x import StdCxx0xCheckTask
			from wonderbuild.std_checks.boost import BoostCheckTask
			from wonderbuild.std_checks.multithreading_support import MultithreadingSupportCheckTask
			from wonderbuild.std_checks.openmp import OpenMPCheckTask
			from wonderbuild.std_checks.dynamic_loading_support import DynamicLoadingSupportCheckTask

			check_cfg = self.cfg.clone()
			std_math = StdMathCheckTask.shared(check_cfg)
			std_cxx0x = StdCxx0xCheckTask.shared(check_cfg)
			boost = BoostCheckTask.shared(check_cfg, (1, 40, 0), ('signals', 'thread', 'filesystem', 'date_time'))
			mt = MultithreadingSupportCheckTask.shared(check_cfg)
			openmp = OpenMPCheckTask.shared(check_cfg)
			dl = DynamicLoadingSupportCheckTask.shared(check_cfg)
			glibmm = PkgConfigCheckTask.shared(check_cfg, ['glibmm-2.4', 'gmodule-2.0', 'gthread-2.0'])

			req = [std_math, boost] # required because pre-compiled.private.hpp include them unconditionaly
			opt = [std_cxx0x, mt, openmp, dl, glibmm]
			for x in sched_ctx.parallel_wait(*(req + opt)): yield x
			self.result = min(bool(r) for r in req)
			self.private_deps += req + [x for x in opt if x]
			for x in PreCompileTasks.__call__(self, sched_ctx): yield x

		def do_cxx_phase(self): self.cfg.include_paths.append(self.top_src_dir / 'build-systems' / 'src')

		source_text = '#include <forced-include.private.hpp>\n'

