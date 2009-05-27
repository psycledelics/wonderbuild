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

class ModPhases(object):
	def __init__(self):
		self.check = None
		self.cxx = None
		self.mod = None

class ModDep(ModPhases):
	def apply_cxx_to(self, cfg): pass
	def apply_private_mod_to(self, cfg): pass
	def apply_public_mod_to(self, cfg): pass

class MultiBuildCheckTask(CheckTask, ModDep):
	def __init__(self):
		self.check = self

	def apply_cxx_to(self, cfg):
		pass
		
	def apply_private_mod_to(self, cfg):
		self.apply_public_mod_to(cfg)

	def apply_public_mod_to(self, cfg):
		pass

class _DoModTask(Task):
	def __init__(self, mod_task):
		self.mod_task = mod_task

	def __call__(self, sched_ctx):
		mod_task = self.mod_task
		sched_ctx.parallel_wait(mod_task)
		sched_ctx.parallel_wait(*mod_task.all_deps) # normally already processed by mod_task
		sched_ctx.parallel_wait(*(dep.cxx for dep in mod_task.all_deps))
		mod_task.do_mod(sched_ctx)
		for dep in all_deps: dep.apply_cxx_to(mod_task.cfg)
		if mod_task.ld:
			t = [dep.mod for dep in mod_task.all_deps]
		t += batches
		sched_ctx.parallel_wait(*t)
		if mod_task.ld:
			for dep in all_deps: dep.apply_private_mod_to(mod_task.cfg)
		mod_task.cfg.impl.process_mod_task(mod_task)

class ModTask(ProjectTask, ModDep):
	def __init__(self, name, kind, base_cfg, *aliases):
		if len(aliases) == 0: aliases = (name,)
		ProjectTask.__init__(self, base_cfg.project, *aliases)
		self.name = name
		self.kind = kind
		self.base_cfg = base_cfg
		self.sources = []
		self.mod = _DoModTask(self)
		self.project.add_task_aliases(self.mod, *self.aliases)
	
	@property
	def all_deps(self): return self.private_deps + self.public_deps
		
	def __call__(self, sched_ctx):
		self.private_deps = [] # of ModDep
		self.public_deps = [] # of ModDep
		self.cxx = None

	def do_mod(self, sched_ctx):
		pass

	def apply_cxx_to(self, cfg):
		if self in cfg.applied: return
		for dep in self.public_deps: dep.apply_cxx_to(cfg)

	def apply_public_mod_to(self, cfg):
		if self in cfg.applied: return
		for dep in self.public_deps: dep.apply_public_mod_to(cfg)
		if not self.target_dev_dir in cfg.lib_paths: cfg.lib_paths.append(self.target_dev_dir)
		cfg.libs.append(self.target_dev_name)

	def apply_private_mod_to(self, cfg):
		if self in cfg.applied: return
		for dep in self.all_deps: dep.apply_private_mod_to(cfg)

from wonderbuild.script import ScriptTask

class Wonderbuild(ScriptTask):
	@property
	def pch(self): return self._pch
	
	@property
	def mod(self): return self._mod

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

		# used by pch too
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

		class Universalis(ModTask):
			def __init__(self):
				ModTask.__init__(self, 'universalis', ModTask.Kinds.LIB, cfg)
				self.check = self
				
			def __call__(self, sched_ctx):
				self.private_deps += [pch.lib_task]
				self.public_deps += [diversalis, std_math, boost]
				sched_ctx.parallel_wait(dlfcn, pthread, glibmm, mswindows, winmm)
				self.public_deps += [x for x in (dlfcn, pthread, glibmm) if x]
				if mswindows:
					if winmm: self.public_deps.append(winmm)
					else: raise UserReadableException, 'on mswindows, universalis requires microsoft\'s windows multimedia extensions: ' + winmm.help
				self.result = True
				self.cxx = UniversalisClientHeaders()
				ModTask.__call__(self, sched_ctx)
			
			def do_mod(self):
				self.cfg.defines['UNIVERSALIS__SOURCE'] = self.cfg.shared and '1' or '-1'
				self.cfg.include_paths.extend([src_dir, src_dir / 'universalis' / 'standard_library' / 'future_std_include'])
				for s in (src_dir / 'universalis').find_iter(in_pats = ('*.cpp',), prune_pats = ('todo',)): self.sources.append(s)
			
			def apply_cxx_to(self, cfg):
				for i in (self.cxx.dest_dir, self.cxx.dest_dir / 'standard_library' / 'future_std_include'):
					if not i in cfg.include_paths: cfg.include_paths.append(i)
				if not self.cfg.shared: cfg.defines['UNIVERSALIS__SOURCE'] = '-1'
				ModTask.apply_cxx_to(self, cfg)
		
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
		
		self._client_headers = headers = UniversalisClientHeaders()
		self._pch = pch = Pch()
		self._mod = mod = Universalis()
		self.project.add_task_aliases(mod, 'universalis', 'all')
		self.project.add_task_aliases(mod.cxx, 'universalis', 'all')
		self.project.add_task_aliases(mod.mod, 'universalis', 'all')
