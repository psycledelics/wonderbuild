#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2009-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from wonderbuild.script import ScriptTask

class Wonderbuild(ScriptTask):
	def __call__(self, sched_ctx):

		project = self.project
		src_dir = self.src_dir / 'src'
		
		from wonderbuild.cxx_tool_chain import UserBuildCfg, PkgConfigCheckTask, ModTask
		from wonderbuild.std_checks import StdMathCheckTask, BoostCheckTask, DlfcnCheckTask, PThreadCheckTask
		from wonderbuild.install import InstallTask
		
		glibmm = PkgConfigCheckTask.shared(self.project, ['glibmm-2.4 >= 2.4'])

		build_cfg = UserBuildCfg.new_or_clone(project)

		check_cfg = build_cfg.clone()
		std_math_check = StdMathCheckTask(check_cfg)
		boost_check = BoostCheckTask(103300, ['signals', 'thread', 'filesystem'], check_cfg)
		dlfcn_check = DlfcnCheckTask(check_cfg)
		pthread_check = PThreadCheckTask(check_cfg)

		diversalis = ScriptTask.shared(project, src_dir.parent.parent / 'diversalis')

		build_cfg.include_paths.append(src_dir)
		build_cfg.include_paths.append(src_dir / 'universalis' / 'standard_library' / 'future_std_include')
		
		class Universalis(ModTask):
			def __init__(self): ModTask.__init__(self, 'universalis', ModTask.Kinds.LIB, build_cfg)

			def __call__(self, sched_ctx):
				install = Universalis.Install(self.project)
				sched_ctx.parallel_no_wait(install)
				sched_ctx.parallel_wait(glibmm, std_math_check, boost_check, dlfcn_check, pthread_check)
				if dlfcn_check.result: dlfcn_check.apply_to(self.cfg)
				if pthread_check.result: pthread_check.apply_to(self.cfg)
				if std_math_check.result: std_math_check.apply_to(self.cfg)
				else: raise Exception, 'need std math'
				if boost_check.result: boost_check.apply_to(self.cfg)
				else: raise Exception, 'need boost'
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
