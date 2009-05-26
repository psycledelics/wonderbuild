#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2009-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

if __name__ == '__main__':
	try: from wonderbuild.main import main
	except ImportError:
		import sys, os
		dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'build-systems'))
		if dir not in sys.path: sys.path.append(dir)
		try: from wonderbuild.main import main
		except ImportError:
			print >> sys.stderr, 'could not find wonderbuild'
			sys.exit(1)
		else: main()
	else: main()

from wonderbuild.script import ScriptTask

class Wonderbuild(ScriptTask):
	@property
	def pch(self): return self._pch
	
	@property
	def client_headers(self): return self._client_headers

	@property
	def client_mod(self): return self._client_mod

	def __call__(self, sched_ctx):
		project = self.project
		top_src_dir = self.src_dir.parent
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
		
		cfg = UserBuildCfg.new_or_clone(project)
		if cfg.kind == 'msvc': # XXX flags are a mess with msvc
			#cfg.defines['WINVER'] = '0x501' # select win xp explicitly because msvc 2008 defaults to vista
			cfg.defines['BOOST_ALL_DYN_LINK'] = None # choose to link against boost dlls
			cfg.cxx_flags += ['-EHa', '-MD'] # basic compilation flags required

		check_cfg = cfg.clone()
		std_math = StdMathCheckTask.shared(check_cfg)
		dlfcn = DlfcnCheckTask.shared(check_cfg)
		pthread = PThreadCheckTask.shared(check_cfg)
		boost = BoostCheckTask.shared((1, 33), ('signals', 'thread', 'filesystem', 'date_time'), check_cfg)
		glibmm = PkgConfigCheckTask.shared(project, ['glibmm-2.4 >= 2.4', 'gmodule-2.0 >= 2.0', 'gthread-2.0 >= 2.0'])
		mswindows = MSWindowsCheckTask.shared(check_cfg)
		winmm = WinMMCheckTask.shared(check_cfg)
		diversalis = ScriptTask.shared(project, src_dir.parent.parent / 'diversalis')

		cfg.defines['UNIVERSALIS__SOURCE'] = cfg.shared and '1' or '-1'
		cfg.include_paths.extend([
			src_dir,
			src_dir / 'universalis' / 'standard_library' / 'future_std_include'
		])

		class Pch(PreCompileTasks):
			def __init__(self): PreCompileTasks.__init__(self, 'pch', cfg)

			@property
			def source_text(self):
				try: return self._source_text
				except AttributeError:
					self._source_text = '#include <pre-compiled.private.hpp>\n'
					return self._source_text

			def __call__(self, sched_ctx):
				sched_ctx.parallel_wait(std_math, dlfcn, pthread, boost, glibmm, diversalis.client_headers)
				
				if std_math: std_math.apply_to(self.cfg)
				else: raise UserReadableException, 'universalis requires the standard math lib: ' + std_math.help

				if boost: boost.apply_to(self.cfg)
				else: raise UserReadableException, 'universalis requires the folowing boost libs: ' + boost.help

				diversalis.client_headers.apply_to(self.cfg)

				for opt in (dlfcn, pthread, glibmm):
					if opt: opt.apply_to(self.cfg)

				self.cfg.include_paths.append(top_src_dir / 'build-systems' / 'src')
				PreCompileTasks.__call__(self, sched_ctx)

		class UniversalisMod(ModTask):
			def __init__(self): ModTask.__init__(self, 'universalis', ModTask.Kinds.LIB, cfg)

			def __call__(self, sched_ctx):
				sched_ctx.parallel_wait(pch.lib_task, mswindows, winmm)
				self.apply_to(self.cfg)
				for x in (pch.lib_task,): x.apply_to(self.cfg)
				for s in (src_dir / 'universalis').find_iter(in_pats = ('*.cpp',), prune_pats = ('todo',)): self.sources.append(s)
				ModTask.__call__(self, sched_ctx)
			
			def apply_to(self, cfg):
				for x in (diversalis.client_headers, std_math, boost): x.apply_to(cfg)
				for x in (dlfcn, pthread, glibmm):
					if x: x.apply_to(cfg)
				if mswindows:
					if winmm: winmm.apply_to(cfg)
					else: raise UserReadableException, 'on mswindows, universalis requires microsoft\'s windows multimedia extensions: ' + winmm.help
			
		class UniversalisClientHeaders(InstallTask):
			def __init__(self): InstallTask.__init__(self, project)

			@property
			def trim_prefix(self): return src_dir

			@property
			def dest_dir(self): return self.fhs.include

			@property
			def sources(self):
				try: return self._sources
				except AttributeError:
					self._sources = []
					for s in (self.trim_prefix / 'universalis').find_iter(
						in_pats = ('*.hpp',), ex_pats = ('*.private.hpp',), prune_pats = ('todo',)): self._sources.append(s)
					for s in (self.trim_prefix / 'universalis' / 'standard_library' / 'future_std_include').find_iter(
						in_pats = ('condition', 'cstdint', 'date_time', 'mutex', 'thread'),
						prune_pats = ('*',)): self._sources.append(s)
					return self._sources
			
			def apply_to(self, cfg):
				if not self.fhs.include in cfg.include_paths: cfg.include_paths.append(self.fhs.include)
				cfg.include_paths.append(self.fhs.include / 'universalis' / 'standard_library' / 'future_std_include')
				if not cfg.shared: cfg.defines['UNIVERSALIS__SOURCE'] = '0'
		
		self._client_headers = headers = UniversalisClientHeaders()
		self._pch = pch = Pch()
		self._mod = mod = UniversalisMod()
		self.project.add_task_aliases(mod, 'all')
		self.project.add_task_aliases(headers, 'universalis', 'all')
