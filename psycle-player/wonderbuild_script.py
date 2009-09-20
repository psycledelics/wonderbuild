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

	def __call__(self, sched_ctx):
		project = self.project
		top_src_dir = self.src_dir.parent
		src_dir = self.src_dir / 'src'

		core = ScriptLoaderTask.shared(project, top_src_dir / 'psycle-core')
		for x in sched_ctx.parallel_wait(core): yield x
		core = core.script_task
		self._common = common = core.common
		core = core.mod_dep_phases
		pch = common.pch
		cfg = common.cfg.new_or_clone()

		from wonderbuild.cxx_tool_chain import PkgConfigCheckTask, ModTask
		from wonderbuild.install import InstallTask

		xml = PkgConfigCheckTask.shared(project, ['libxml++-2.6'])

		class PlayerMod(ModTask):
			def __init__(self):
				name = 'psycle-player'
				ModTask.__init__(self, name, ModTask.Kinds.PROG, cfg, (name, 'default'))

			def __call__(self, sched_ctx):
				self.private_deps = [pch.prog_task, core]
				req = self.all_deps
				opt = [xml]
				for x in sched_ctx.parallel_wait(*(req + opt)): yield x
				self.result = min(bool(r) for r in req)
				self.private_deps += [o for o in opt if o]
				for x in ModTask.__call__(self, sched_ctx): yield x

			def do_mod_phase(self):
				if xml: self.cfg.defines['PSYCLE__LIBXMLPP_AVAILABLE'] = None
				self.cfg.include_paths.appendleft(src_dir)
				for s in (src_dir / 'psycle' / 'player').find_iter(
					in_pats = ('*.cpp',), prune_pats = ('todo',)
				): self.sources.append(s)

		player = PlayerMod()
