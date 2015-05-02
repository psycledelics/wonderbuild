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
	def __call__(self, sched_ctx):
		project = self.project
		top_src_dir = self.src_dir.parent.parent
		src_dir = self.src_dir
		default_tasks = self.default_tasks

		from wonderbuild.cxx_tool_chain import UserBuildCfgTask, PkgConfigCheckTask
		from wonderbuild.cxx_tool_chain import ModTask
		from wonderbuild.install import InstallTask

		cfg = UserBuildCfgTask.shared(project)
		for x in sched_ctx.parallel_wait(cfg): yield x
		self._cfg = cfg = cfg.clone()

		check_cfg = cfg.clone()
		gtkglextmm = PkgConfigCheckTask.shared(check_cfg, ['gtkglextmm-1.2 >= 1.2'])

		class UniformMod(ModTask):
			def __init__(self, name, path, deps=None, kind=ModTask.Kinds.LOADABLE):
				ModTask.__init__(self, name, kind, cfg)
				self.path = path
				if deps is not None: self.public_deps += deps
				if kind in (ModTask.Kinds.PROG, ModTask.Kinds.LOADABLE): default_tasks.append(self.mod_phase)

			def do_set_deps(self, sched_ctx):
				if False: yield
				self.private_deps = [gtkglextmm]
				self.cxx_phase = self.__class__.InstallHeaders(self)
			
			def do_mod_phase(self):
				self.cfg.include_paths.appendleft(src_dir)
				if self.path.exists:
					for s in self.path.find_iter(in_pats = ('*.cpp',), prune_pats = ('todo',)): self.sources.append(s)
				else: self.sources.append(self.path.parent / (self.path.name + '.cpp'))

			def apply_cxx_to(self, cfg):
				if not self.cxx_phase.dest_dir in cfg.include_paths: cfg.include_paths.append(self.cxx_phase.dest_dir)
				ModTask.apply_cxx_to(self, cfg)

			class InstallHeaders(InstallTask):
				def __init__(self, outer):
					InstallTask.__init__(self, outer.base_cfg.project, outer.name + '-headers')
					self.outer = outer
					
				@property
				def trim_prefix(self): return src_dir

				@property
				def dest_dir(self): return self.fhs.include

				@property
				def sources(self):
					try: return self._sources
					except AttributeError:
						self._sources = []
						if self.outer.path.exists:
							for s in self.outer.path.find_iter(
								in_pats = ('*.hpp',), ex_pats = ('*.private.hpp',), prune_pats = ('todo',)): self._sources.append(s)
						f = self.outer.path.parent / (self.outer.path.name + '.hpp')
						if f.exists: self._sources.append(f)
						return self._sources

		UniformMod('simple', src_dir / 'simple', kind=ModTask.Kinds.PROG)
		UniformMod('simple-mixed', src_dir / 'simple_mixed', kind=ModTask.Kinds.PROG)
		UniformMod('pixmap', src_dir / 'pixmap', kind=ModTask.Kinds.PROG)
		UniformMod('pixmap-mixed', src_dir / 'pixmap_mixed', kind=ModTask.Kinds.PROG)
		UniformMod('font', src_dir / 'font', kind=ModTask.Kinds.PROG)
		UniformMod('coolwave2', src_dir / 'coolwave2', kind=ModTask.Kinds.PROG)