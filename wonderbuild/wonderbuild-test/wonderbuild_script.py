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

			def __call__(self, sched_ctx):
				self.public_deps = [std_math, glibmm]
				req = self.public_deps
				opt = std_math, glibmm
				sched_ctx.parallel_wait(*opt)
				self.result = True
				self.public_deps += [x for x in opt if x]
				PreCompileTasks.__call__(self, sched_ctx)
			
			def do_cxx(self):
				self.source_text
				if std_math: self._source_text += '\n#include <cmath>'
				if glibmm: self._source_text += '\n#include <glibmm.h>'

			@property
			def source_text(self):
				try: return self._source_text
				except AttributeError:
					self._source_text = \
						'#include <string>\n' \
						'#include <sstream>\n' \
						'#include <iostream>'
					return self._source_text
		pch = Pch()

		class LibFoo(ModTask):
			def __init__(self): ModTask.__init__(self, 'foo', ModTask.Kinds.LIB, build_cfg)

			def __call__(self, sched_ctx):
				self.private_deps = [pch.lib_task]
				req = self.private_deps
				opt = [std_math, glibmm]
				sched_ctx.parallel_wait(*(req + opt))
				self.result = min(req)
				self.public_deps += [x for x in opt if x]
				self.cxx = LibFoo.Install(self.project, self.name + '-headers')
				ModTask.__call__(self, sched_ctx)
				
			def do_mod(self):
				for s in (src_dir / 'foo').find_iter(in_pats = ('*.cpp',), prune_pats = ('todo',)): self.sources.append(s)

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
				self.public_deps = [lib_foo]
				req = self.public_deps
				opt = [glibmm]
				sched_ctx.parallel_wait(*(req + opt))
				self.result = min(req)
				self.public_deps += [x for x in opt if x]
				ModTask.__call__(self, sched_ctx)
				
			def do_mod(self):
				for s in (src_dir / 'main').find_iter(in_pats = ['*.cpp'], prune_pats = ['todo']): self.sources.append(s)
		main_prog = MainProg()
