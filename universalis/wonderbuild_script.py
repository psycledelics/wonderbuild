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
	def mod_dep_phases(self): return self._mod_dep_phases

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
		boost = BoostCheckTask.shared((1, 35), ('signals', 'thread', 'filesystem', 'date_time'), check_cfg)
		glibmm = PkgConfigCheckTask.shared(project, ['glibmm-2.4 >= 2.4', 'gmodule-2.0 >= 2.0', 'gthread-2.0 >= 2.0'])
		mswindows = MSWindowsCheckTask.shared(check_cfg)
		winmm = WinMMCheckTask.shared(check_cfg)
		diversalis = ScriptTask.shared(project, src_dir.parent.parent / 'diversalis').mod_dep_phases

		class Pch(PreCompileTasks):
			def __init__(self): PreCompileTasks.__init__(self, 'pch', cfg)

			@property
			def source_text(self):
				try: return self._source_text
				except AttributeError:
					self._source_text = '#include <pre-compiled.private.hpp>\n'
					return self._source_text

			def __call__(self, sched_ctx):
				self.public_deps = [diversalis, std_math, boost]
				req = self.public_deps
				opt = [dlfcn, pthread, glibmm]
				sched_ctx.parallel_wait(universalis.cxx, *(req + opt))
				self.result = min(req)
				self.public_deps += [x for x in opt if x]
				for i in (universalis.cxx.dest_dir, universalis.cxx.dest_dir / 'universalis' / 'standard_library' / 'future_std_include'):
					if not i in self.cfg.include_paths: self.cfg.include_paths.append(i)
				self.cfg.include_paths.append(top_src_dir / 'build-systems' / 'src')
				PreCompileTasks.__call__(self, sched_ctx)
			
			def do_cxx(self):
				if not std_math: raise UserReadableException, 'universalis requires the standard math lib: ' + std_math.help
				if not boost: raise UserReadableException, 'universalis requires the folowing boost libs: ' + boost.help

		class UniversalisMod(ModTask):
			def __init__(self):
				ModTask.__init__(self, 'universalis', ModTask.Kinds.LIB, cfg, 'universalis', 'default')
				self.cxx = UniversalisMod.InstallHeaders(self.project, self.name + '-headers')
				
			def __call__(self, sched_ctx):
				self.private_deps = [pch.lib_task]
				self.public_deps = [diversalis, std_math, boost]
				req = self.public_deps + self.private_deps
				opt = [dlfcn, pthread, glibmm]
				sched_ctx.parallel_no_wait(winmm)
				sched_ctx.parallel_wait(mswindows, *(req + opt))
				self.result = min(req)
				self.public_deps += [x for x in opt if x]
				if self.result and mswindows:
					sched_ctx.wait(winmm)
					if winmm: self.public_deps.append(winmm)
					else: self.result = False
				ModTask.__call__(self, sched_ctx)
			
			def do_mod(self):
				if not std_math: raise UserReadableException, 'universalis requires the standard math lib: ' + std_math.help
				if not boost: raise UserReadableException, 'universalis requires the folowing boost libs: ' + boost.help
				if mswindows and not winmm: raise UserReadableException, 'on mswindows, universalis requires microsoft\'s windows multimedia extensions: ' + winmm.help
				self.cfg.defines['UNIVERSALIS__SOURCE'] = self.cfg.shared and '1' or '-1'
				self.cfg.include_paths.extend([src_dir, src_dir / 'universalis' / 'standard_library' / 'future_std_include'])
				for s in (src_dir / 'universalis').find_iter(in_pats = ('*.cpp',), prune_pats = ('todo',)): self.sources.append(s)
			
			def apply_cxx_to(self, cfg):
				for i in (self.cxx.dest_dir, self.cxx.dest_dir / 'universalis' / 'standard_library' / 'future_std_include'):
					if not i in cfg.include_paths: cfg.include_paths.append(i)
				if not self.cfg.shared: cfg.defines['UNIVERSALIS__SOURCE'] = '-1'
				ModTask.apply_cxx_to(self, cfg)
		
			class InstallHeaders(InstallTask):
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
		
		self._pch = pch = Pch()
		self._mod_dep_phases = mod_dep_phases = universalis = UniversalisMod()
