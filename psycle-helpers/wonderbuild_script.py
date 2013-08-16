#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2009-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

if __name__ == '__main__':
	import sys, os
	dir = os.path.dirname(__file__)
	sys.argv.append('--src-dir=' + dir)
	try: from wonderbuild.main import main
	except ImportError:
		dir = os.path.abspath(os.path.join(dir, os.pardir, 'build-systems', 'wonderbuild'))
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
		top_src_dir = self.src_dir.parent
		src_dir = self.src_dir / 'src'

		universalis = ScriptLoaderTask.shared(self.project, top_src_dir / 'universalis')
		for x in sched_ctx.parallel_wait(universalis): yield x
		universalis = universalis.script_task
		self._common = common = universalis.common
		universalis = universalis.mod_dep_phases
		pch = common.pch
		cfg = common.cfg.clone()

		from wonderbuild.cxx_tool_chain import UserBuildCfgTask, ModTask, PkgConfigCheckTask
		from wonderbuild.std_checks.std_math import StdMathCheckTask
		from wonderbuild.std_checks.boost import BoostCheckTask
		from wonderbuild.install import InstallTask

		check_cfg = cfg.clone()
		std_math = StdMathCheckTask.shared(check_cfg)
		soxr = PkgConfigCheckTask.shared(check_cfg, ['soxr >= 0.1.1'])
		boost_test = BoostCheckTask.shared(check_cfg, (1, 40, 0), ('unit_test_framework',))

		class HelpersMathMod(ModTask):
			def __init__(self):
				name = 'psycle-helpers-math'
				ModTask.__init__(self, name, ModTask.Kinds.HEADERS, cfg,
					cxx_phase = self.__class__.InstallHeaders(cfg.project, name + '-headers'))
				
			def __call__(self, sched_ctx):
				self.private_deps = [pch.lib_task]
				self.public_deps = [universalis, std_math]
				req = self.all_deps
				for x in sched_ctx.parallel_wait(*req): yield x
				self.result = min(bool(r) for r in req)

			class InstallHeaders(InstallTask):
				@property
				def trim_prefix(self): return src_dir

				@property
				def dest_dir(self): return self.fhs.include

				@property
				def sources(self):
					try: return self._sources
					except AttributeError:
						self._sources = [self.trim_prefix / 'psycle' / 'helpers' / 'math.hpp'] + \
							list((self.trim_prefix / 'psycle' / 'helpers' / 'math').find_iter(
								in_pats = ('*.hpp',), ex_pats = ('*.private.hpp',), prune_pats = ('todo',)))
						return self._sources
						
			def apply_cxx_to(self, cfg):
				if not self.cxx_phase.dest_dir in cfg.include_paths: cfg.include_paths.append(self.cxx_phase.dest_dir)

		self._math_mod_dep_phases = helpers_math = HelpersMathMod()
		self.default_tasks.append(helpers_math.cxx_phase)

		class HelpersMod(ModTask):
			def __init__(self): ModTask.__init__(self, 'psycle-helpers', ModTask.Kinds.LIB, cfg)

			def __call__(self, sched_ctx):
				self.private_deps = [pch.lib_task]
				self.public_deps = [universalis, helpers_math, soxr]
				req = self.all_deps
				for x in sched_ctx.parallel_wait(*req): yield x
				self.result = min(bool(r) for r in req)
				self.cxx_phase = HelpersMod.InstallHeaders(self.base_cfg.project, self.name + '-headers')

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
							in_pats = ('*.hpp',), ex_pats = ('*.private.hpp', 'math.hpp'), prune_pats = ('todo', 'math')): self._sources.append(s)
						return self._sources

			def apply_cxx_to(self, cfg):
				if not self.cxx_phase.dest_dir in cfg.include_paths: cfg.include_paths.append(self.cxx_phase.dest_dir)

			def do_mod_phase(self):
				self.cfg.include_paths.appendleft(src_dir)
				self.cfg.defines['UNIVERSALIS__META__MODULE__NAME'] = '"' + self.name +'"'
				self.cfg.defines['UNIVERSALIS__META__MODULE__VERSION'] = 0
				for s in (src_dir / 'psycle' / 'helpers').find_iter(in_pats = ('*.cpp',), prune_pats = ('todo', 'math')): self.sources.append(s)

		self._mod_dep_phases = helpers = HelpersMod()
		self.default_tasks.append(helpers.mod_phase)
						
		class UnitTestMod(ModTask):
			def __init__(self): ModTask.__init__(self, 'psycle-helpers-unit-tests', ModTask.Kinds.PROG, cfg)

			def __call__(self, sched_ctx):
				self.private_deps = [pch.prog_task, helpers, boost_test]
				req = self.all_deps
				for x in sched_ctx.parallel_wait(*req): yield x
				self.result = min(bool(r) for r in req)

			def do_mod_phase(self):
				self.cfg.include_paths.appendleft(src_dir)
				self.cfg.defines['UNIVERSALIS__META__MODULE__NAME'] = '"' + self.name +'"'
				self.cfg.defines['UNIVERSALIS__META__MODULE__VERSION'] = 0
				self.sources.append(src_dir / 'unit_tests.cpp')
				
		unit_tests = UnitTestMod()
		for x in sched_ctx.parallel_wait(boost_test): yield x
		if boost_test: self.default_tasks.append(unit_tests.mod_phase)
