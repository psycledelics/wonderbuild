#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2009-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from wonderbuild.script import ScriptTask

class Wonderbuild(ScriptTask):
	def __call__(self, sched_ctx):

		project = self.project
		src_dir = self.src_dir / 'src'
		
		from wonderbuild import UserReadableException
		from wonderbuild.cxx_tool_chain import UserBuildCfg, PkgConfigCheckTask, PreCompileTasks, ModTask
		from wonderbuild.std_checks import MSWindowsCheckTask
		from wonderbuild.std_checks.std_math import StdMathCheckTask
		from wonderbuild.std_checks.dlfcn import DlfcnCheckTask
		from wonderbuild.std_checks.pthread import PThreadCheckTask
		from wonderbuild.std_checks.boost import BoostCheckTask
		from wonderbuild.std_checks.winmm import WinMMCheckTask
		from wonderbuild.install import InstallTask
		
		glibmm = PkgConfigCheckTask.shared(self.project, ['glibmm-2.4 >= 2.4'])

		build_cfg = UserBuildCfg.new_or_clone(project)

		check_cfg = build_cfg.clone()
		std_math = StdMathCheckTask.shared(check_cfg)
		dlfcn = DlfcnCheckTask.shared(check_cfg)
		pthread = PThreadCheckTask.shared(check_cfg)
		boost = BoostCheckTask.shared((1, 33), ['signals', 'thread', 'filesystem'], check_cfg)
		mswindows = MSWindowsCheckTask.shared(check_cfg)
		winmm = WinMMCheckTask.shared(check_cfg)

		diversalis = ScriptTask.shared(project, src_dir.parent.parent / 'diversalis')

		build_cfg.include_paths.append(src_dir)
		build_cfg.include_paths.append(src_dir / 'universalis' / 'standard_library' / 'future_std_include')
		build_cfg.defines['UNIVERSALIS__SOURCE'] = build_cfg.shared and '1' or '-1'
		
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
				sched_ctx.parallel_wait(std_math, dlfcn, pthread, boost, glibmm)
				self.source_text
				if std_math:
					std_math.apply_to(self.cfg)
					self._source_text += '\n#include <cmath>'
				if dlfcn:
					dlfcn.apply_to(self.cfg)
					self._source_text += '\n#include <dlfcn.h>'
				if pthread:
					pthread.apply_to(self.cfg)
					self._source_text += '\n#include <pthread.h>'
				if boost:
					boost.apply_to(self.cfg)
					self._source_text += '\n#include <boost/thread.hpp>'
					self._source_text += '\n#include <boost/filesystem/path.hpp>'
					self._source_text += '\n#include <boost/signals.hpp>'
				if glibmm:
					glibmm.apply_to(self.cfg)
					self._source_text += '\n#include <glibmm.h>'
				PreCompileTasks.__call__(self, sched_ctx)
		pch = Pch()

		class Universalis(ModTask):
			def __init__(self): ModTask.__init__(self, 'universalis', ModTask.Kinds.LIB, build_cfg)

			def __call__(self, sched_ctx):
				install = Universalis.Install(self.project)
				sched_ctx.parallel_no_wait(install)
				sched_ctx.parallel_wait(pch.lib_task, mswindows, winmm)
				pch.lib_task.apply_to(self.cfg)
				if dlfcn: dlfcn.apply_to(self.cfg)
				if pthread: pthread.apply_to(self.cfg)

				if std_math: std_math.apply_to(self.cfg)
				else: raise UserReadableException, 'universalis requires the standard math lib: ' + std_math.help

				if boost: boost.apply_to(self.cfg)
				else: raise UserReadableException, 'universalis requires the folowing boost libs: ' + boost.help

				if glibmm: glibmm.apply_to(self.cfg)

				if mswindows:
					if winmm: winmm.apply_to(self.cfg)
					else: raise UserReadableException, 'on mswindows, universalis requires microsoft\'s windows multimedia extensions: ' + winmm.help

				#sched_ctx.parallel_wait(diversalis.install)
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
					self._client_cfg.include_paths.append(src_dir / 'universalis' / 'standard_library' / 'future_std_include')
					if not self.cfg.shared: self._client_cfg.defines['UNIVERSALIS__SOURCE'] = '0'
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
						for s in (self.trim_prefix / 'universalis').find_iter(
								in_pats = ('*.hpp',),
								ex_pats = ('*.private.hpp',),
								prune_pats = ('todo',)
							): self._sources.append(s)
						for s in (self.trim_prefix / 'universalis' / 'standard_library' / 'future_std_include').find_iter(
								in_pats = ('condition', 'cstdint', 'date_time', 'mutex', 'thread'),
								prune_pats = ('*',)
							): self._sources.append(s)
						return self._sources
		
				@property
				def dest_dir(self): return self.fhs.include

		universalis = Universalis()

		self.project.add_task_aliases(universalis, 'all')
