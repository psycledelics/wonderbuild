#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2010-2010 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

if __name__ == '__main__':
	import sys, os
	dir = os.path.dirname(__file__)
	sys.argv.append('--src-dir=' + dir)
	try: from wonderbuild.main import main
	except ImportError:
		dir = os.path.abspath(os.path.join(dir, os.pardir, os.pardir, os.pardir, 'build-systems', 'wonderbuild'))
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

		from wonderbuild.cxx_tool_chain import UserBuildCfgTask
		from wonderbuild.cxx_tool_chain import ModTask
		from wonderbuild.std_checks.opengl import OpenGLCheckTask
		from wonderbuild.install import InstallTask

		cfg = UserBuildCfgTask.shared(project)
		for x in sched_ctx.parallel_wait(cfg): yield x
		self._cfg = cfg = cfg.clone()

		check_cfg = cfg.clone()
		gl = OpenGLCheckTask.shared(check_cfg)

		# Note: the language must not be changed in the check_cfg because checks are shared with other scripts via cfg.shared_checks,
		# and they may not want them done in objective-c++.
		# We can change the language after cloning the check_cfg,
		# but that's unneeded since g++ autodetects that files with a .mm extension must be compiled as objective-c++.
		cfg.lang = 'objective-c++'
		cfg.libs.append('objc')
		cfg.frameworks += ['UIKit', 'CoreFoundation', 'Foundation', 'CoreGraphics', 'QuartzCore']

		class UniformMod(ModTask):
			def __init__(self, name, path, deps=None, kind=ModTask.Kinds.LOADABLE):
				ModTask.__init__(self, name, kind, cfg)
				self.path = path
				if deps is not None: self.public_deps += deps
				if kind in (ModTask.Kinds.PROG, ModTask.Kinds.LOADABLE): default_tasks.append(self.mod_phase)

			def __call__(self, sched_ctx):
				self.private_deps = [gl]
				#if self.kind == ModTask.Kinds.PROG: self.private_deps.append(pch.prog_task)
				#else: self.private_deps.append(pch.lib_task)
				#self.public_deps += []
				req = self.all_deps
				for x in sched_ctx.parallel_wait(*req): yield x
				self.result = min(bool(r) for r in req)
				self.cxx_phase = self.__class__.InstallHeaders(self)
				for x in ModTask.__call__(self, sched_ctx): yield x
			
			def do_mod_phase(self):
				self.cfg.include_paths.appendleft(src_dir)
				if self.path.exists:
					for s in self.path.find_iter(in_pats = ('*.mm', '*.m'), prune_pats = ('todo',)): self.sources.append(s)
				else:
					f = self.path.parent / (self.path.name + '.mm')
					if not f.exists: f = self.path.parent / (self.path.name + '.m')
					self.sources.append(f)

			def apply_cxx_to(self, cfg):
				if not self.cxx_phase.dest_dir in cfg.include_paths: cfg.include_paths.append(self.cxx_phase.dest_dir)
				ModTask.apply_cxx_to(self, cfg)

			class InstallHeaders(InstallTask):
				def __init__(self, outer):
					InstallTask.__init__(self, outer.project, outer.name + '-headers')
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
								in_pats = ('*.hpp', '*.h'), ex_pats = ('*.private.hpp', '*.private.h'), prune_pats = ('todo',)): self._sources.append(s)
						f = self.outer.path.parent / (self.outer.path.name + '.hpp')
						if not f.exists: f = self.outer.path.parent / (self.outer.path.name + '.h')
						if f.exists: self._sources.append(f)
						return self._sources

		UniformMod('eagl-test', src_dir / 'test', kind=ModTask.Kinds.PROG)
		UniformMod('eagl-neheihpone-02', src_dir / 'neheiphone' / 'NeHe Lesson 02', kind=ModTask.Kinds.PROG)
