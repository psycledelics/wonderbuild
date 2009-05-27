#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2009-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

if __name__ == '__main__':
	try: from wonderbuild.main import main
	except ImportError:
		import sys, os
		dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'build-systems'))
		if dir not in sys.path: sys.path.append(dir)
		try: from wonderbuild.main import main
		except ImportError:
			print >> sys.stderr, 'could not find wonderbuild'
			sys.exit(1)
		else: main()
	else: main()

from wonderbuild.script import ScriptTask

class Wonderbuild(ScriptTask):
	def __call__(self, sched_ctx):
		project = self.project
		top_src_dir = self.src_dir.parent
		src_dir = self.src_dir / 'src'

		from wonderbuild import UserReadableException
		from wonderbuild.cxx_tool_chain import UserBuildCfg, PkgConfigCheckTask, PreCompileTasks, ModTask
		from wonderbuild.std_checks import MSWindowsCheckTask
		from wonderbuild.std_checks.winmm import WinMMCheckTask
		from wonderbuild.install import InstallTask

		cfg = UserBuildCfg.new_or_clone(project)
		if cfg.kind == 'msvc': # XXX flags are a mess with msvc
			#cfg.defines['WINVER'] = '0x501' # select win xp explicitly because msvc 2008 defaults to vista
			cfg.defines['BOOST_ALL_DYN_LINK'] = None # choose to link against boost dlls
			cfg.cxx_flags += ['-EHa', '-MD'] # basic compilation flags required

		check_cfg = cfg.clone()
		universalis = ScriptTask.shared(project, src_dir.parent.parent / 'universalis')

		class Helpers(ModTask):
			def __init__(self): ModTask.__init__(self, 'psycle-helpers', ModTask.Kinds.LIB, cfg)

			def __call__(self, sched_ctx):
				#sched_ctx.parallel_wait(pch.lib_task, universalis.mod)
				#self.apply_to(self.cfg)
				#for x in (pch.lib_task, universalis.mod): x.apply_to(self.cfg)
				for s in (src_dir / 'psycle' / 'helpers').find_iter(in_pats = ('*.cpp',), prune_pats = ('todo',)): self.sources.append(s)
				ModTask.__call__(self, sched_ctx)
			
			def apply_to(self, cfg):
				for x in (universalis.client_cxx_cfg): x.apply_to(cfg)
				for x in (dlfcn, pthread, glibmm):
					if x: x.apply_to(cfg)
				if mswindows:
					if winmm: winmm.apply_to(cfg)
					else: raise UserReadableException, 'on mswindows, universalis requires microsoft\'s windows multimedia extensions: ' + winmm.help
		helpers = Helpers()
		self.project.add_task_aliases(helpers, 'all')
