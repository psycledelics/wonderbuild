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

		for x in sched_ctx.parallel_wait(gstreamer, jack, alsa, dsound, gtkmm, gnomecanvas): yield x

		class UniformModule(ModTask):
			def __init__(self, path, name, *deps):
				ModTask.__init__(self, name, ModTask.Kinds.LIB, cfg, name, 'default')
				self.path = path
				self.public_deps += deps

			def __call__(self, sched_ctx):
				self.private_deps = [pch.lib_task]
				self.public_deps += [universalis, helpers_math]
				req = self.all_deps
				for x in sched_ctx.parallel_wait(*req): yield x
				self.result = min(bool(r) for r in req)
				self.cxx_phase = self.__class__.InstallHeaders(self)
				for x in ModTask.__call__(self, sched_ctx): yield x
			
			def do_mod_phase(self):
				self.cfg.include_paths.appendleft(src_dir)
				if self.path.exists:
					for s in self.path.find_iter(in_pats = ('*.cpp',), prune_pats = ('todo')): self.sources.append(s)
				else: self.sources.append(self.path.parent / (self.path.name + '.cpp'))

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
								in_pats = ('*.hpp',), ex_pats = ('*.private.hpp',), prune_pats = ('todo')): self._sources.append(s)
						else: self._sources = [self.outer.path.parent / (self.outer.path.name + '.hpp')]
						return self._sources

		paths = UniformModule(src_dir / 'psycle' / 'paths', 'freepsycle-path')
		engine = UniformModule(src_dir / 'psycle' / 'engine', 'freepsycle-engine')
		host = UniformModule(src_dir / 'psycle' / 'host', 'freepsycle-host')
		stream = UniformModule(src_dir / 'psycle' / 'stream', 'freepsycle-stream')
		bipolar_filter = UniformModule(src_dir / 'psycle' / 'plugins' / 'bipolar_filter', 'freepsycle-plugin-bipolar-filter', engine)
		resource = UniformModule(src_dir / 'psycle' / 'plugins' / 'resource', 'freepsycle-plugin-resource', engine)
		decay = UniformModule(src_dir / 'psycle' / 'plugins' / 'decay', 'freepsycle-plugin-decay', engine)
		sequence = UniformModule(src_dir / 'psycle' / 'plugins' / 'sequence', 'freepsycle-plugin-sequence', engine)
		sine = UniformModule(src_dir / 'psycle' / 'plugins' / 'sine', 'freepsycle-plugin-sine', engine)
		additioner = UniformModule(src_dir / 'psycle' / 'plugins' / 'additioner', 'freepsycle-plugin-additioner', engine)
		multiplier = UniformModule(src_dir / 'psycle' / 'plugins' / 'multiplier', 'freepsycle-plugin-multiplier', engine)
		if dsound: dsound_output = UniformModule(src_dir / 'psycle' / 'plugins' / 'outputs'/ 'direct_sound', 'freepsycle-plugin-outputs-microsoft-direct-sound', resource)

		#class Output
		#default_output
		#class MSDirectSoundOutput
		#class GStreamerOutput
		#class AlsaOutput
		#class JackOutput
		#class DummyOutput
		#class TextFrontEnd
		#class GUIFrontEnd
