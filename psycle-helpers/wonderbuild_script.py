#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2009-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

if __name__ == '__main__':
	import sys, os
	dir = os.path.dirname(__file__)
	sys.argv.append('--src-dir=' + dir)
	try: from wonderbuild.main import main
	except ImportError:
		dir = os.path.abspath(os.path.join(dir, os.pardir, 'build-systems'))
		if dir not in sys.path: sys.path.append(dir)
		try: from wonderbuild.main import main
		except ImportError:
			print >> sys.stderr, 'could not find wonderbuild'
			sys.exit(1)
		else: main()
	else: main()

from wonderbuild.script import ScriptTask, ScriptLoaderTask

class Wonderbuild(ScriptTask):
	@property
	def common(self): return self._common

	@property
	def mod_dep_phases(self): return self._mod_dep_phases
	
	@property
	def math_mod_dep_phases(self): return self._math_mod_dep_phases

	def __call__(self, sched_ctx):
		project = self.project
		top_src_dir = self.src_dir.parent
		src_dir = self.src_dir / 'src'

		universalis = ScriptLoaderTask.shared(project, top_src_dir / 'universalis')
		for x in sched_ctx.parallel_wait(universalis): yield x
		universalis = universalis.script_task
		self._common = common = universalis.common
		universalis = universalis.mod_dep_phases
		pch = common.pch
		cfg = common.cfg.new_or_clone()

		from wonderbuild.cxx_tool_chain import UserBuildCfgTask, ModTask
		from wonderbuild.std_checks.std_math import StdMathCheckTask
		from wonderbuild.std_checks.boost import BoostCheckTask
		from wonderbuild.install import InstallTask

		cfg = UserBuildCfgTask.shared(project)
		for x in sched_ctx.parallel_wait(cfg): yield x
		cfg = cfg.new_or_clone()
		
		check_cfg = cfg.clone()
		std_math = StdMathCheckTask.shared(check_cfg)
		boost_test = BoostCheckTask.shared((1, 33), ('unit_test_framework',), check_cfg)

		class HelpersMathMod(ModTask):
			def __init__(self): ModTask.__init__(self, 'psycle-helpers-math', ModTask.Kinds.HEADERS, cfg, 'psycle-helpers-math', 'default',
				cxx_phase=HelpersMathMod.InstallHeaders()
			)
				
			def __call__(self, sched_ctx):
				self.private_deps = [pch.lib_task]
				self.public_deps = [universalis, std_math]
				for x in ModTask.__call__(self, sched_ctx): yield x
				req = self.all_deps
				self.result = min(bool(r) for r in req)

			def apply_cxx_to(self, cfg):
				if not self.cxx_phase.dest_dir in cfg.include_paths: cfg.include_paths.append(self.cxx_phase.dest_dir)
				ModTask.apply_cxx_to(self, cfg)

			class InstallHeaders(InstallTask):
				def __init__(self): InstallTask.__init__(self, project, 'psycle-helpers-math-headers')

				@property
				def trim_prefix(self): return src_dir

				@property
				def dest_dir(self): return self.fhs.include

				@property
				def sources(self):
					try: return self._sources
					except AttributeError:
						self._sources = list((self.trim_prefix / 'psycle' / 'helpers' / 'math').find_iter(
							in_pats = ('*.hpp',), ex_pats = ('*.private.hpp',), prune_pats = ('todo',)))
						return self._sources

		class HelpersMod(ModTask):
			def __init__(self): ModTask.__init__(self, 'psycle-helpers', ModTask.Kinds.LIB, cfg, 'psycle-helpers', 'default')

			def __call__(self, sched_ctx):
				self.private_deps = [pch.lib_task]
				self.public_deps = [universalis, helpers_math]
				req = self.all_deps
				for x in sched_ctx.parallel_wait(*req): yield x
				self.result = min(bool(r) for r in req)
				self.cxx_phase = HelpersMod.InstallHeaders(self.project, self.name + '-headers')
				for x in ModTask.__call__(self, sched_ctx): yield x

			def do_ensure_deps(self):
				if not std_math: raise UserReadableException, self.name + ' requires the standard math lib: ' + std_math.help

			def do_mod_phase(self):
				self.cfg.include_paths.appendleft(src_dir)
				for s in (src_dir / 'psycle' / 'helpers').find_iter(in_pats = ('*.cpp',), prune_pats = ('todo', 'math')): self.sources.append(s)

			def apply_cxx_to(self, cfg):
				if not self.cxx_phase.dest_dir in cfg.include_paths: cfg.include_paths.append(self.cxx_phase.dest_dir)
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
						for s in (self.trim_prefix / 'psycle' / 'helpers').find_iter(
							in_pats = ('*.hpp',), ex_pats = ('*.private.hpp',), prune_pats = ('todo', 'math')): self._sources.append(s)
						return self._sources
						
		class UnitTestMod(ModTask):
			def __init__(self): ModTask.__init__(self, 'psycle-helpers-unit-tests', ModTask.Kinds.PROG, cfg, 'psycle-helpers-unit-tests', 'default')

			def __call__(self, sched_ctx):
				self.private_deps = [pch.prog_task, universalis, boost_test]
				req = self.all_deps
				for x in sched_ctx.parallel_wait(*req): yield x
				self.result = min(bool(r) for r in req)
				for x in ModTask.__call__(self, sched_ctx): yield x

			def do_mod_phase(self):
				self.cfg.include_paths.appendleft(src_dir)
				self.sources.append(src_dir / 'unit_tests.cpp')

		self._math_mod_dep_phases = helpers_math = HelpersMathMod()
		self._mod_dep_phases = mod_dep_phases = HelpersMod()
		for x in sched_ctx.parallel_wait(boost_test): yield x
		if boost_test: unit_tests = UnitTestMod()
