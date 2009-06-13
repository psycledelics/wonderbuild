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

from wonderbuild.script import ScriptTask, ScriptLoaderTask

class Wonderbuild(ScriptTask):

	def __call__(self, sched_ctx):
		project = self.project
		top_src_dir = self.src_dir.parent
		src_dir = self.src_dir / 'src'

		universalis = ScriptLoaderTask.shared(project, top_src_dir / 'universalis')
		helpers = ScriptLoaderTask.shared(project, top_src_dir / 'psycle-helpers')
		for x in sched_ctx.parallel_wait(universalis, helpers): yield x
		universalis = universalis.script_task
		pch = universalis.pch
		universalis = universalis.mod_dep_phases
		helpers_math = helpers.script_task.math_mod_dep_phases

		from wonderbuild import UserReadableException
		from wonderbuild.cxx_tool_chain import UserBuildCfg, PkgConfigCheckTask, ModTask
		from wonderbuild.std_checks.dsound import DSoundCheckTask
		from wonderbuild.std_checks import MSWindowsCheckTask
		from wonderbuild.std_checks.winmm import WinMMCheckTask
		from wonderbuild.install import InstallTask

		gstreamer = PkgConfigCheckTask.shared(project, ['gstreamer-0.10 >= 0.10', 'gstreamer-plugins-base-0.10 >= 0.10'])
		jack = PkgConfigCheckTask.shared(project, ['jack >= 0.101.1'])
		alsa = PkgConfigCheckTask.shared(project, ['alsa >= 1.0'])
		gtkmm = PkgConfigCheckTask.shared(project, ['gtkmm-2.4 >= 2.4'])
		gnomecanvas = PkgConfigCheckTask.shared(project, ['libgnomecanvasmm-2.6 >= 2.6'])

		cfg = UserBuildCfg.new_or_clone(project)
		for x in sched_ctx.parallel_wait(cfg): yield x
		
		if cfg.kind == 'msvc': # XXX flags are a mess with msvc
			#cfg.defines['WINVER'] = '0x501' # select win xp explicitly because msvc 2008 defaults to vista
			cfg.defines['BOOST_ALL_DYN_LINK'] = None # choose to link against boost dlls
			cfg.cxx_flags += ['-EHa', '-MD'] # basic compilation flags required

		check_cfg = cfg.clone()
		dsound = DSoundCheckTask.shared(check_cfg)

		#class Path
		#class Engine
		#class Host
		#class Stream
		#class BipolarFilter
		#class Resource
		#class Plugin
		#class Decay
		#class Sequence
		#class Sine
		#class Additioner
		#class Multiplier
		#class Output
		#default_output
		#class MSDirectSoundOutput
		#class GStreamerOutput
		#class AlsaOutput
		#class JackOutput
		#class DummyOutput
		#class TextFrontEnd
		#class GUIFrontEnd
