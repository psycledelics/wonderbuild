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

	def __call__(self, sched_ctx):
		project = self.project
		top_src_dir = self.src_dir.parent
		src_dir = self.src_dir / 'src'
		
		diversalis = ScriptLoaderTask.shared(project, top_src_dir / 'diversalis')
		for x in sched_ctx.parallel_wait(diversalis): yield x
		diversalis = diversalis.script_task
		self._common = common = diversalis.common
		diversalis = diversalis.mod_dep_phases
		cfg = common.cfg.clone()

		from wonderbuild.cxx_tool_chain import PkgConfigCheckTask, ModTask
		from wonderbuild.std_checks.std_math import StdMathCheckTask
		from wonderbuild.std_checks.std_cxx0x import StdCxx0xCheckTask
		from wonderbuild.std_checks.boost import BoostCheckTask
		from wonderbuild.std_checks.multithreading_support import MultithreadingSupportCheckTask
		from wonderbuild.std_checks.openmp import OpenMPCheckTask
		from wonderbuild.std_checks.dynamic_loading_support import DynamicLoadingSupportCheckTask
		from wonderbuild.std_checks.winmm import WinMMCheckTask

		check_cfg = cfg.clone()
		std_math = StdMathCheckTask.shared(check_cfg)
		std_cxx0x = StdCxx0xCheckTask.shared(check_cfg)
		boost = BoostCheckTask.shared(check_cfg, (1, 40, 0), ('signals', 'thread', 'filesystem', 'date_time'))
		boost_test = BoostCheckTask.shared(check_cfg, (1, 40, 0), ('unit_test_framework',))
		mt = MultithreadingSupportCheckTask.shared(check_cfg)
		openmp = OpenMPCheckTask.shared(check_cfg)
		dl = DynamicLoadingSupportCheckTask.shared(check_cfg)
		glibmm = PkgConfigCheckTask.shared(check_cfg, ['glibmm-2.4', 'gmodule-2.0', 'gthread-2.0'])
		winmm = WinMMCheckTask.shared(check_cfg)
		
		CommonPch = common.Pch
		class Pch(CommonPch):
			def __call__(self, sched_ctx):
				for x in CommonPch.__call__(self, sched_ctx): yield x
				req = [diversalis]
				opt = []
				for x in sched_ctx.parallel_wait(universalis.cxx_phase, *(req + opt)): yield x
				self.result = self.result and min(bool(r) for r in req)
				self.public_deps += req + [x for x in opt if x]
			
			def do_cxx_phase(self):
				if universalis.cxx_phase.dest_dir not in self.cfg.include_paths: self.cfg.include_paths.append(universalis.cxx_phase.dest_dir)
				CommonPch.do_cxx_phase(self)
		common.__class__.Pch = Pch # overrides the common pch
		pch = common.pch

		from wonderbuild import UserReadableException
		from wonderbuild.install import InstallTask

		class UniversalisMod(ModTask):
			def __init__(self):
				name = 'universalis'
				ModTask.__init__(self, name, ModTask.Kinds.LIB, cfg)
				self.cxx_phase = UniversalisMod.InstallHeaders(self.project, self.name + '-headers')
				
			def __call__(self, sched_ctx):
				self.private_deps = [pch.lib_task]
				self.public_deps = [diversalis, std_math, boost, mt, dl]
				if self.cfg.dest_platform.os == 'win': self.public_deps.append(winmm)
				req = self.public_deps + self.private_deps
				opt = [std_cxx0x, openmp, glibmm]
				for x in sched_ctx.parallel_wait(*(req + opt)): yield x
				self.result = min(bool(r) for r in req)
				self.public_deps += [x for x in opt if x]
				for x in ModTask.__call__(self, sched_ctx): yield x

			def do_ensure_deps(self):
				if not boost: raise UserReadableException, self.name + ' requires the following boost libs: ' + boost.help
				if self.cfg.dest_platform.os == 'win' and not winmm: raise UserReadableException, \
					'on mswindows, ' + self.name + ' requires microsoft\'s windows multimedia extensions: ' + winmm.help
				ModTask.do_ensure_deps(self)
			
			def do_mod_phase(self):
				if self.cfg.shared: self.cfg.defines['UNIVERSALIS__SHARED'] = None
				self.cfg.defines['UNIVERSALIS__META__MODULE__NAME'] = '"' + self.name +'"'
				self.cfg.defines['UNIVERSALIS__META__MODULE__VERSION'] = 0
				self.cfg.include_paths.appendleft(src_dir)
				for s in (src_dir / 'universalis').find_iter(in_pats = ('*.cpp',), prune_pats = ('todo',)): self.sources.append(s)
			
			def apply_cxx_to(self, cfg):
				if self.cxx_phase.dest_dir not in cfg.include_paths: cfg.include_paths.append(self.cxx_phase.dest_dir)
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
						self._sources = [self.trim_prefix / 'universalis.hpp'] + \
							list((self.trim_prefix / 'universalis').find_iter(
								in_pats = ('*.hpp',), ex_pats = ('*.private.hpp',), prune_pats = ('todo',)))
						return self._sources
		self._mod_dep_phases = mod_dep_phases = universalis = UniversalisMod()
		self.default_tasks.append(mod_dep_phases.mod_phase)

		class UnitTestMod(ModTask):
			def __init__(self):
				name = 'universalis-unit-tests'
				ModTask.__init__(self, name, ModTask.Kinds.PROG, cfg)

			def __call__(self, sched_ctx):
				self.private_deps = [pch.prog_task, universalis, boost_test]
				req = self.all_deps
				for x in sched_ctx.parallel_wait(*req): yield x
				self.result = min(bool(r) for r in req)
				for x in ModTask.__call__(self, sched_ctx): yield x

			def do_mod_phase(self):
				self.cfg.include_paths.appendleft(src_dir)
				self.cfg.defines['UNIVERSALIS__META__MODULE__NAME'] = '"' + self.name +'"'
				self.cfg.defines['UNIVERSALIS__META__MODULE__VERSION'] = 0
				self.sources.append(src_dir / 'unit_tests.cpp')
		for x in sched_ctx.parallel_wait(boost_test): yield x
		if boost_test:
			unit_tests = UnitTestMod()
			self.default_tasks.append(unit_tests.mod_phase)
