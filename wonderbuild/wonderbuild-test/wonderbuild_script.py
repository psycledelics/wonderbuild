#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from wonderbuild.script import ScriptTask

class Wonderbuild(ScriptTask):
	def __call__(self, sched_ctx):

		lib_hello = ScriptTask.shared(self.project, self.src_dir / 'libhello')
		print 'sub script tasks:', lib_hello.dummy

		src_dir = self.src_dir / 'src'

		from wonderbuild.cxx_tool_chain import UserBuildCfg, PkgConfigCheckTask, BuildCheckTask, PreCompileTasks, ModTask
		from wonderbuild.std_checks.std_math import StdMathCheckTask
		from wonderbuild.install import InstallTask
	
		glibmm = PkgConfigCheckTask.shared(self.project, ['glibmm-2.4 >= 2.4'])

		build_cfg = UserBuildCfg.new_or_clone(self.project)

		check_cfg = build_cfg.clone()
		std_math = StdMathCheckTask.shared(check_cfg)

		build_cfg.include_paths.append(src_dir)

		class Pch(PreCompileTasks):
			def __init__(self): PreCompileTasks.__init__(self, 'pch', build_cfg)

			@property
			def source_text(self):
				try: return self._source_text
				except AttributeError:
					self._source_text = \
						'#include <string>\n' \
						'#include <sstream>\n' \
						'#include <iostream>'
					return self._source_text

			def __call__(self, sched_ctx):
				sched_ctx.parallel_wait(std_math, glibmm)
				self.source_text
				if std_math:
					std_math.apply_cxx_to(self.cfg)
					self._source_text += '\n#include <cmath>'
				if glibmm:
					glibmm.apply_cxx_to(self.cfg)
					self._source_text += '\n#include <glibmm.h>'
				PreCompileTasks.__call__(self, sched_ctx)
		pch = Pch()

		class LibFoo(ModTask):
			def __init__(self): ModTask.__init__(self, 'foo', ModTask.Kinds.LIB, build_cfg)

			def __call__(self, sched_ctx):
				ModTask.__call__(self, sched_ctx)
				self.private_deps += [pch.lib_task]
				sched_ctx.parallel_wait(std_math, glibmm)
				for opt in (std_math, glibmm):
					if opt: self.public_deps.append(opt)
				for s in (src_dir / 'foo').find_iter(in_pats = ('*.cpp',), prune_pats = ('todo',)): self.sources.append(s)
				self.cxx = LibFoo.Install(self.project)

			def apply_cxx_to(self, cfg):
				if not self.cxx.dest_dir in cfg.include_paths: cfg.include_paths.append(self.cxx.dest_dir)

			class Install(InstallTask):
				@property
				def trim_prefix(self): return src_dir

				@property
				def sources(self):
					try: return self._sources
					except AttributeError:
						self._sources = []
						for s in (self.trim_prefix / 'foo').find_iter(in_pats = ('*.hpp',), ex_pats = ('*.private.hpp',), prune_pats = ('todo',)): self._sources.append(s)
						return self._sources
		
				@property
				def dest_dir(self): return self.fhs.include
		lib_foo = LibFoo()
	
		class MainProg(ModTask):
			def __init__(self): ModTask.__init__(self, 'main', ModTask.Kinds.PROG, build_cfg, 'default')

			def __call__(self, sched_ctx):
				ModTask.__call__(self, sched_ctx)
				self.public_deps += [lib_foo]
				self.private_deps += [pch.prog_task]
				sched_ctx.parallel_wait(glibmm)
				for opt in (glibmm,):
					if opt: self.public_deps.append(opt)
				for s in (src_dir / 'main').find_iter(in_pats = ['*.cpp'], prune_pats = ['todo']): self.sources.append(s)
		main_prog = MainProg()
