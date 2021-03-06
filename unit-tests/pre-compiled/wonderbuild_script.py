#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2015 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

if __name__ == '__main__':
	import sys, os
	dir = os.path.dirname(__file__)
	sys.argv.append('--src-dir=' + dir)
	try: from wonderbuild.main import main
	except ImportError:
		dir = os.path.abspath(os.path.join(dir, os.pardir, os.pardir))
		if dir not in sys.path: sys.path.append(dir)
		try: from wonderbuild.main import main
		except ImportError:
			print >> sys.stderr, 'could not import wonderbuild module with path', sys.path
			sys.exit(1)
		else: main()
	else: main()

from wonderbuild.script import ScriptTask, ScriptLoaderTask

class Wonderbuild(ScriptTask):
	def __call__(self, sched_ctx):

		test_name = self.src_dir.name
		src_dir = self.src_dir / 'src'

		from wonderbuild.cxx_tool_chain import UserBuildCfgTask, PkgConfigCheckTask, BuildCheckTask, PreCompileTasks, ModTask
		from wonderbuild.std_checks.std_math import StdMathCheckTask
		from wonderbuild.install import InstallTask

		cfg = UserBuildCfgTask.shared(self.project)
		for x in sched_ctx.parallel_wait(cfg): yield x
		cfg = cfg.clone()
		if not src_dir in cfg.include_paths: cfg.include_paths.append(src_dir)

		check_cfg = cfg.clone()
		std_math = StdMathCheckTask.shared(check_cfg)

		pe = cfg.dest_platform.bin_fmt == 'pe'

		if not pe: glibmm = PkgConfigCheckTask.shared(check_cfg, ['glibmm-2.4 >= 2.4'])

		class Pch(PreCompileTasks):
			def __init__(self): PreCompileTasks.__init__(self, 'pch', cfg)

			def do_set_deps(self, sched_ctx):
				self.public_deps = [std_math]
				req = self.public_deps
				opt = []
				if not pe: opt += [glibmm]
				for x in sched_ctx.parallel_wait(*(req + opt)): yield x
				self.public_deps += [x for x in opt if x]
			
			def do_cxx_phase(self):
				self.source_text
				self._source_text += '\n#include <cmath>'
				if not pe and glibmm: self._source_text += '\n#include <glibmm.h>'

			@property
			def source_text(self):
				try: return self._source_text
				except AttributeError:
					self._source_text = \
						'#include <string>\n' \
						'#include <sstream>\n' \
						'#include <iostream>'
					return self._source_text
		pch = Pch()

		class LibImpl(ModTask):
			def __init__(self): ModTask.__init__(self, test_name + '--impl', ModTask.Kinds.LIB, cfg)

			def do_set_deps(self, sched_ctx):
				self.private_deps = [pch.lib_task]
				req = self.private_deps
				opt = [std_math]
				if not pe: opt += [glibmm]
				for x in sched_ctx.parallel_wait(*(req + opt)): yield x
				self.public_deps += [x for x in opt if x]
				self.cxx_phase = self.__class__.Install(self.cfg.project, self.name + '-headers')
				
			def do_mod_phase(self):
				self.cfg.defines['IMPL'] = self.cfg.shared and '1' or '-1'
				for s in (src_dir / 'impl').find_iter(('*.cpp',)): self.sources.append(s)

			def apply_cxx_to(self, cfg):
				if not self.cxx_phase.dest_dir in cfg.include_paths: cfg.include_paths.append(self.cxx_phase.dest_dir)
				if not self.cfg.shared: cfg.defines['IMPL'] = '-1'

			class Install(InstallTask):
				@property
				def trim_prefix(self): return src_dir

				@property
				def sources(self):
					try: return self._sources
					except AttributeError:
						self._sources = []
						for s in (self.trim_prefix / 'impl').find_iter(('*.hpp',)): self._sources.append(s)
						return self._sources
		
				@property
				def dest_dir(self): return self.fhs.include / test_name
		lib_impl = LibImpl()
	
		class LibWrapper(ModTask):
			def __init__(self): ModTask.__init__(self, test_name + '--wrapper', ModTask.Kinds.LIB, cfg)

			def do_set_deps(self, sched_ctx):
				self.public_deps = [lib_impl]
				self.private_deps = [pch.lib_task]
				req = self.public_deps + self.private_deps
				opt = [std_math]
				if not pe: opt += [glibmm]
				for x in sched_ctx.parallel_wait(*(req + opt)): yield x
				self.public_deps += [x for x in opt if x]
				self.cxx_phase = self.__class__.Install(self.cfg.project, self.name + '-headers')
				
			def do_mod_phase(self):
				self.cfg.defines['WRAPPER'] = self.cfg.shared and '1' or '-1'
				for s in (src_dir / 'wrapper').find_iter(('*.cpp',)): self.sources.append(s)

			def apply_cxx_to(self, cfg):
				if not self.cxx_phase.dest_dir in cfg.include_paths: cfg.include_paths.append(self.cxx_phase.dest_dir)
				if not self.cfg.shared: cfg.defines['WRAPPER'] = '-1'

			class Install(InstallTask):
				@property
				def trim_prefix(self): return src_dir

				@property
				def sources(self):
					try: return self._sources
					except AttributeError:
						self._sources = []
						for s in (self.trim_prefix / 'wrapper').find_iter(('*.hpp',)): self._sources.append(s)
						return self._sources
		
				@property
				def dest_dir(self): return self.fhs.include / test_name
		lib_wrapper = LibWrapper()

		class MainProg(ModTask):
			def __init__(self): ModTask.__init__(self, test_name + '--main', ModTask.Kinds.PROG, cfg)

			def do_set_deps(self, sched_ctx):
				self.public_deps = [lib_wrapper]
				self.private_deps = [pch.prog_task]
				req = self.public_deps + self.private_deps
				opt = []
				if not pe: opt += [glibmm]
				for x in sched_ctx.parallel_wait(*(req + opt)): yield x
				self.public_deps += [x for x in opt if x]
				
			def do_mod_phase(self):
				for s in (src_dir / 'main').find_iter(('*.cpp',)): self.sources.append(s)
		main_prog = MainProg()
		self.default_tasks.append(main_prog.mod_phase)
