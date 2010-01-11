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

		common = ScriptLoaderTask.shared(project, top_src_dir / 'build-systems' / 'wonderbuild' / 'wonderbuild_script_common')
		for x in sched_ctx.parallel_wait(common): yield x
		self._common = common = common.script_task
		cfg = common.cfg.clone()

		from wonderbuild.cxx_tool_chain import ModTask
		from wonderbuild.install import InstallTask

		class DiversalisMod(ModTask):
			def __init__(self):
				name = 'diversalis'
				ModTask.__init__(self, name, ModTask.Kinds.HEADERS, cfg, (name, 'default'), cxx_phase=DiversalisMod.InstallHeaders())
				
			def __call__(self, sched_ctx):
				self.result = True
				for x in ModTask.__call__(self, sched_ctx): yield x
			
			def apply_cxx_to(self, cfg):
				if not self.cxx_phase.dest_dir in cfg.include_paths: cfg.include_paths.append(self.cxx_phase.dest_dir)
				ModTask.apply_cxx_to(self, cfg)

			class InstallHeaders(InstallTask):
				def __init__(self): InstallTask.__init__(self, project, 'diversalis-headers')

				@property
				def trim_prefix(self): return src_dir

				@property
				def dest_dir(self): return self.fhs.include

				@property
				def sources(self):
					try: return self._sources
					except AttributeError:
						self._sources = list((self.trim_prefix / 'diversalis').find_iter(
							in_pats = ('*.hpp',), ex_pats = ('*.private.hpp',), prune_pats = ('todo',)))
						return self._sources
		
		self._mod_dep_phases = mod_dep_phases = DiversalisMod()
