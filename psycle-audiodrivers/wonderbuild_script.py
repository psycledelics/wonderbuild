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

	@property
	def mod_dep_phases(self): return self._mod_dep_phases

	def __call__(self, sched_ctx):
		project = self.project
		top_src_dir = self.src_dir.parent
		src_dir = self.src_dir / 'src'

		helpers = ScriptLoaderTask.shared(project, src_dir.parent.parent / 'psycle-helpers')
		pch = ScriptLoaderTask.shared(project, src_dir.parent.parent / 'universalis')
		for x in sched_ctx.parallel_wait(helpers, pch): yield x
		helpers = helpers.script_task.mod_dep_phases
		pch = pch.script_task.pch

		from wonderbuild.cxx_tool_chain import UserBuildCfg, PkgConfigCheckTask, ModTask
		from wonderbuild.std_checks.winmm import WinMMCheckTask
		from wonderbuild.std_checks.dsound import DSoundCheckTask
		from wonderbuild.install import InstallTask

		alsa = PkgConfigCheckTask.shared(project, ['alsa >= 1.0'])
		jack = PkgConfigCheckTask.shared(project, ['jack >= 0.101.1'])
		esound = PkgConfigCheckTask.shared(project, ['esound'])
		gstreamer = PkgConfigCheckTask.shared(project, ['gstreamer-0.10 >= 0.10 gstreamer-plugins-base-0.10 >= 0.10'])

		cfg = UserBuildCfg.new_or_clone(project)
		for x in sched_ctx.parallel_wait(cfg): yield x
		
		if cfg.kind == 'msvc': # XXX flags are a mess with msvc
			#cfg.defines['WINVER'] = '0x501' # select win xp explicitly because msvc 2008 defaults to vista
			cfg.defines['BOOST_ALL_DYN_LINK'] = None # choose to link against boost dlls
			cfg.cxx_flags += ['-EHa', '-MD'] # basic compilation flags required

		check_cfg = cfg.clone()
		winmm = WinMMCheckTask.shared(check_cfg)
		dsound = DSoundCheckTask.shared(check_cfg)

		class AudioDriversMod(ModTask):
			def __init__(self): ModTask.__init__(self, 'psycle-audiodrivers', ModTask.Kinds.LIB, cfg, 'psycle-audiodrivers', 'default')

			def __call__(self, sched_ctx):
				self.private_deps = [pch.lib_task]
				self.public_deps = [helpers]
				req = self.public_deps + self.private_deps
				opt = [alsa, jack, esound, dsound, winmm] # gstreamer, netaudio, asio
				for x in sched_ctx.parallel_wait(*(req + opt)): yield x
				self.result = min(req)
				self.public_deps += [o for o in opt if o]
				self.cxx_phase = AudioDriversMod.InstallHeaders(self.project, self.name + '-headers')
				for x in ModTask.__call__(self, sched_ctx): yield x

			def _apply_defines(self, cfg):
				d = cfg.defines
				if alsa:   d['PSYCLE__ALSA_AVAILABLE'] = None
				if jack:   d['PSYCLE__JACK_AVAILABLE'] = None
				if esound: d['PSYCLE__ESOUND_AVAILABLE'] = None
				if dsound: d['PSYCLE__MICROSOFT_DIRECT_SOUND_AVAILABLE'] = None
				if winmm:  d['PSYCLE__MICROSOFT_MME_AVAILABLE'] = None
				if False:
					if gstreamer: d['PSYCLE__GSTREAMER_AVAILABLE'] = None
					if netaudio:  d['PSYCLE__NET_AUDIO_AVAILABLE'] = None
					if asio:      d['PSYCLE__STEINBERG_ASIO_AVAILABLE'] = None
			
			def do_mod_phase(self):
				self.cfg.include_paths.appendleft(src_dir)
				self._apply_defines(self.cfg)
				s = self.sources
				dir = src_dir / 'psycle' / 'audiodrivers'
				s.append(dir / 'audiodriver.cpp')
				s.append(dir / 'wavefileout.cpp')
				if alsa:   s.append(dir / 'alsaout.cpp')
				if jack:   s.append(dir / 'jackout.cpp')
				if esound: s.append(dir / 'esoundout.cpp')
				if dsound: s.append(dir / 'microsoftdirectsoundout.cpp')
				if winmm:  s.append(dir / 'microsoftmmewaveout.cpp')
				if False:
					if gstreamer: s.append(dir / 'gstreamerout.cpp')
					if netaudio:  s.append(dir / 'netaudioout.cpp')
					if asio:      s.append(dir / 'asioout.cpp')

			def apply_cxx_to(self, cfg):
				if not self.cxx_phase.dest_dir in cfg.include_paths: cfg.include_paths.append(self.cxx_phase.dest_dir)
				self._apply_defines(cfg)
				ModTask.apply_cxx_to(self, cfg)

			class InstallHeaders(InstallTask):
				@property
				def trim_prefix(self): return src_dir

				@property
				def dest_dir(self): return self.fhs.include

				@property
				def sources(self):
					try: return self._sources
					except AttributeError:
						self._sources = s = []
						dir = src_dir / 'psycle' / 'audiodrivers'
						s.append(dir / 'audiodriver.h')
						s.append(dir / 'wavefileout.h')
						if alsa:   s.append(dir / 'alsaout.h')
						if jack:   s.append(dir / 'jackout.h')
						if esound: s.append(dir / 'esoundout.h')
						if dsound: s.append(dir / 'microsoftdirectsoundout.h')
						if winmm:  s.append(dir / 'microsoftmmewaveout.h')
						if False:
							if gstreamer: s.append(dir / 'gstreamerout.h')
							if netaudio:  s.append(dir / 'netaudioout.h')
							if asio:      s.append(dir / 'asioout.h')
						return s

		self._mod_dep_phases = mod_dep_phases = AudioDriversMod()
