#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

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
			print >> sys.stderr, 'could not find wonderbuild'
			sys.exit(1)
		else: main()
	else: main()

from wonderbuild.script import ScriptTask, ScriptLoaderTask

class Wonderbuild(ScriptTask):
	def __call__(self, sched_ctx):

		src_dir = self.src_dir.parent / 'src'

		from wonderbuild.cxx_tool_chain import UserBuildCfgTask, ModTask
		from wonderbuild.install import InstallTask
	
		build_cfg = UserBuildCfgTask.shared(self.project)
		for x in sched_ctx.parallel_wait(build_cfg): sched_ctx = yield x
		build_cfg = build_cfg.new_or_clone()

		build_cfg.include_paths.append(src_dir)
		
		# dependencies: MainProg -> LibWrapper -> LibImpl

		class LibImpl(ModTask):
			def __init__(self): ModTask.__init__(self, 'impl', ModTask.Kinds.LIB, build_cfg)

			def __call__(self, sched_ctx):
				self.result = True
				self.cxx_phase = LibImpl.Install(self.project, self.name + '-headers')
				for x in ModTask.__call__(self, sched_ctx): yield x

			def do_mod_phase(self):
				for s in (src_dir / 'impl').find_iter(in_pats = ('*.cpp',)): self.sources.append(s)

			def apply_cxx_to(self, cfg):
				if not self.cxx_phase.dest_dir in cfg.include_paths: cfg.include_paths.append(self.cxx_phase.dest_dir)

			class Install(InstallTask):
				@property
				def trim_prefix(self): return src_dir

				@property
				def sources(self):
					try: return self._sources
					except AttributeError:
						self._sources = []
						for s in (self.trim_prefix / 'impl').find_iter(in_pats = ('*.hpp',), ex_pats = ('*.private.hpp',)): self._sources.append(s)
						return self._sources
		
				@property
				def dest_dir(self): return self.fhs.include
		lib_impl = LibImpl()

		class LibWrapper(ModTask):
			def __init__(self): ModTask.__init__(self, 'wrapper', ModTask.Kinds.LIB, build_cfg)

			def __call__(self, sched_ctx):
				self.private_deps = [lib_impl]
				self.result = True
				self.cxx_phase = LibWrapper.Install(self.project, self.name + '-headers')
				for x in ModTask.__call__(self, sched_ctx): yield x

			def do_mod_phase(self):
				for s in (src_dir / 'wrapper').find_iter(in_pats = ('*.cpp',)): self.sources.append(s)

			def apply_cxx_to(self, cfg):
				if not self.cxx_phase.dest_dir in cfg.include_paths: cfg.include_paths.append(self.cxx_phase.dest_dir)

			class Install(InstallTask):
				@property
				def trim_prefix(self): return src_dir

				@property
				def sources(self):
					try: return self._sources
					except AttributeError:
						self._sources = []
						for s in (self.trim_prefix / 'wrapper').find_iter(in_pats = ('*.hpp',), ex_pats = ('*.private.hpp',)): self._sources.append(s)
						return self._sources
		
				@property
				def dest_dir(self): return self.fhs.include
		lib_wrapper = LibWrapper()

		class MainProg(ModTask):
			def __init__(self): ModTask.__init__(self, 'main', ModTask.Kinds.PROG, build_cfg, 'default')

			def __call__(self, sched_ctx):
				self.public_deps = [lib_wrapper]
				for x in ModTask.__call__(self, sched_ctx): yield x
				
			def do_mod_phase(self):
				for s in (src_dir / 'main').find_iter(in_pats = ('*.cpp',)): self.sources.append(s)
		main_prog = MainProg()
