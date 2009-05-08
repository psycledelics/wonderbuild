#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2009-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from wonderbuild.script import ScriptTask

class Wonderbuild(ScriptTask):
	def __call__(self, sched_ctx):

		project = self.project
		src_dir = self.src_dir / 'src'
		
		from wonderbuild.cxx_chain import UserBuildCfg, PkgConfigCheckTask, ModTask
		from wonderbuild.std_checks import StdMathCheckTask
		from wonderbuild.install import InstallTask
		
		glibmm = PkgConfigCheckTask(self.project, ['glibmm-2.4 >= 2.4'])

		try: build_cfg = project.build_cfg
		except AttributeError: build_cfg = project.build_cfg = UserBuildCfg(project)
		else: build_cfg = build_cfg.clone()
		build_cfg.include_paths.append(src_dir)

		check_cfg = build_cfg.clone()
		std_math_check = StdMathCheckTask(check_cfg)

		diversalis = self.project.script_task(src_dir.parent.parent / 'diversalis')
		
		class Universalis(ModTask):
			def __init__(self):
				ModTask.__init__(self, 'universalis', ModTask.Kinds.LIB, build_cfg)

			def __call__(self, sched_ctx):
				install = Universalis.Install(self.project)
				sched_ctx.parallel_no_wait(install)
				sched_ctx.parallel_wait(glibmm, std_math_check)
				if std_math_check.result: std_math_check.apply_to(self.cfg)
				if glibmm.result: glibmm.apply_to(self.cfg)
				diversalis.client_cfg.apply_to(self.cfg)
				for s in (src_dir / 'universalis').find_iter(in_pats = ('*.cpp',), prune_pats = ('todo',)): self.sources.append(s)
				ModTask.__call__(self, sched_ctx)
				sched_ctx.wait(install)

			@property
			def client_cfg(self):
				try: return self._client_cfg
				except AttributeError:
					from wonderbuild.cxx_chain import ClientCfg
					self._client_cfg = ClientCfg(self.project)
					self._client_cfg.include_paths.append(src_dir)
					diversalis.client_cfg.apply_to(self._client_cfg)
					return self._client_cfg
			
			class Install(InstallTask):
				@property
				def trim_prefix(self): return src_dir

				@property
				def sources(self):
					try: return self._sources
					except AttributeError:
						self._sources = []
						for s in (self.trim_prefix / 'universalis').find_iter(in_pats = ('*.hpp',), ex_pats = ('*.private.hpp',), prune_pats = ('todo',)): self._sources.append(s)
						return self._sources
		
				@property
				def dest_dir(self): return self.fhs.include

		universalis = Universalis()

		self.project.add_task_aliases(universalis, 'all')
