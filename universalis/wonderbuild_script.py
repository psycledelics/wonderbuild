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

		from wonderbuild import UserReadableException
		from wonderbuild.cxx_tool_chain import PkgConfigCheckTask, PreCompileTasks, ModTask
		from wonderbuild.std_checks.std_math import StdMathCheckTask
		from wonderbuild.std_checks.dlfcn import DlfcnCheckTask
		from wonderbuild.std_checks.pthread import PThreadCheckTask
		from wonderbuild.std_checks.boost import BoostCheckTask
		from wonderbuild.std_checks.winmm import WinMMCheckTask
		from wonderbuild.install import InstallTask
		
		check_cfg = cfg.clone()
		glibmm = PkgConfigCheckTask.shared(check_cfg, ['glibmm-2.4', 'gmodule-2.0', 'gthread-2.0'])
		std_math = StdMathCheckTask.shared(check_cfg)
		dlfcn = DlfcnCheckTask.shared(check_cfg)
		pthread = PThreadCheckTask.shared(check_cfg)
		boost = BoostCheckTask.shared(check_cfg, (1, 38), ('signals', 'thread', 'filesystem', 'date_time'))
		boost_test = BoostCheckTask.shared(check_cfg, (1, 38), ('unit_test_framework',))
		winmm = WinMMCheckTask.shared(check_cfg)

		class Pch(PreCompileTasks):
			def __init__(self): PreCompileTasks.__init__(self, 'pch', cfg)

			def __call__(self, sched_ctx):
				self.public_deps = [diversalis]
				req = self.public_deps
				opt = [dlfcn, pthread, glibmm, std_math, boost]
				for x in sched_ctx.parallel_wait(universalis.cxx_phase, *(req + opt)): yield x
				self.result = min(bool(r) for r in req)
				self.public_deps += [x for x in opt if x]
				for x in PreCompileTasks.__call__(self, sched_ctx): yield x
			
			def do_cxx_phase(self):
				if universalis.cxx_phase.dest_dir not in self.cfg.include_paths: self.cfg.include_paths.append(universalis.cxx_phase.dest_dir)
				self.cfg.include_paths.append(top_src_dir / 'build-systems' / 'src')

			@property
			def source_text(self):
				try: return self._source_text
				except AttributeError:
					s = '#include <forced-include.private.hpp>'
					if boost: s += '\n#include <pre-compiled/boost.private.hpp>'
					if std_math: s += '\n#include <cmath>'
					self._source_text = s
					return s

		class UniversalisMod(ModTask):
			def __init__(self):
				name = 'universalis'
				ModTask.__init__(self, name, ModTask.Kinds.LIB, cfg, (name, 'default'))
				self.cxx_phase = UniversalisMod.InstallHeaders(self.project, self.name + '-headers')
				
			def __call__(self, sched_ctx):
				self.private_deps = [pch.lib_task]
				self.public_deps = [diversalis, boost]
				req = self.public_deps + self.private_deps
				opt = [dlfcn, pthread, glibmm]
				sched_ctx.parallel_no_wait(winmm)
				for x in sched_ctx.parallel_wait(*(req + opt)): yield x
				self.result = min(bool(r) for r in req)
				self.public_deps += [x for x in opt if x]
				if self.result and self.cfg.dest_platform.os == 'win':
					for x in sched_ctx.parallel_wait(winmm): yield x
					if winmm: self.public_deps.append(winmm)
					else: self.result = False
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
				self.cfg.include_paths.append(src_dir)
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

		class UnitTestMod(ModTask):
			def __init__(self):
				name = 'universalis-unit-tests'
				ModTask.__init__(self, name, ModTask.Kinds.PROG, cfg, (name, 'default'))

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
		
		common._pch = pch = Pch() # overrides the common pch
		self._mod_dep_phases = mod_dep_phases = universalis = UniversalisMod()
		for x in sched_ctx.parallel_wait(boost_test): yield x
		if boost_test: unit_tests = UnitTestMod()
