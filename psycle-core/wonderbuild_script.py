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

	def __call__(self, sched_ctx):
		project = self.project
		top_src_dir = self.src_dir.parent
		src_dir = self.src_dir / 'src'

		audiodrivers = ScriptLoaderTask.shared(project, top_src_dir / 'psycle-audiodrivers')
		for x in sched_ctx.parallel_wait(audiodrivers): yield x
		audiodrivers = audiodrivers.script_task
		self._common = common = audiodrivers.common
		audiodrivers = audiodrivers.mod_dep_phases
		pch = common.pch
		cfg = common.cfg.new_or_clone()

		from wonderbuild.cxx_tool_chain import PkgConfigCheckTask, ModTask
		from wonderbuild.std_checks.zlib import ZLibCheckTask
		from wonderbuild.install import InstallTask

		xml = PkgConfigCheckTask.shared(project, ['libxml++-2.6'])

		check_cfg = cfg.clone()
		zlib = ZLibCheckTask.shared(check_cfg)

		class CoreMod(ModTask):
			def __init__(self): ModTask.__init__(self, 'psycle-core', ModTask.Kinds.LIB, cfg, 'psycle-core', 'default')

			def __call__(self, sched_ctx):
				self.private_deps = [pch.lib_task]
				self.public_deps = [audiodrivers, xml, zlib]
				req = self.public_deps + self.private_deps
				for x in sched_ctx.parallel_wait(*req): yield x
				self.result = min(bool(r) for r in req)
				self.cxx_phase = CoreMod.InstallHeaders(self.project, self.name + '-headers')
				for x in ModTask.__call__(self, sched_ctx): yield x
			
			def apply_cxx_to(self, cfg):
				if not self.cxx_phase.dest_dir in cfg.include_paths: cfg.include_paths.append(self.cxx_phase.dest_dir)
				ModTask.apply_cxx_to(self, cfg)

			def do_mod_phase(self):
				self.cfg.include_paths.appendleft(src_dir)
				self.cfg.include_paths.appendleft(top_src_dir / 'psycle-plugins' / 'src')
				for s in (src_dir / 'psycle' / 'core').find_iter(
					in_pats = ('*.cpp',), prune_pats = ('todo',), ex_pats = ('psy4filter.cpp',)
				): self.sources.append(s)

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
						for s in (self.trim_prefix / 'psycle' / 'core').find_iter(
							in_pats = ('*.hpp', '*.h'), ex_pats = ('*.private.hpp', '*.private.h'), prune_pats = ('todo',)): self._sources.append(s)
						return self._sources

		self._mod_dep_phases = mod_dep_phases = CoreMod()
