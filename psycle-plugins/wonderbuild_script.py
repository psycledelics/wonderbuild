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
		from wonderbuild.install import InstallTask

		cfg = UserBuildCfg.new_or_clone(project)
		for x in sched_ctx.parallel_wait(cfg): yield x
		
		if cfg.kind == 'msvc': # XXX flags are a mess with msvc
			#cfg.defines['WINVER'] = '0x501' # select win xp explicitly because msvc 2008 defaults to vista
			cfg.defines['BOOST_ALL_DYN_LINK'] = None # choose to link against boost dlls
			cfg.cxx_flags += ['-EHa', '-MD'] # basic compilation flags required

		class UniformMod(ModTask):
			def __init__(self, name, path, deps=None, kind=ModTask.Kinds.LOADABLE):
				ModTask.__init__(self, name, kind, cfg, name, 'default')
				self.path = path
				if deps is not None: self.public_deps += deps

			def __call__(self, sched_ctx):
				if self.kind == ModTask.Kinds.PROG: self.private_deps = [pch.prog_task]
				else: self.private_deps = [pch.lib_task]
				self.public_deps += [universalis, helpers_math]
				req = self.all_deps
				for x in sched_ctx.parallel_wait(*req): yield x
				self.result = min(bool(r) for r in req)
				if self.kind == ModTask.Kinds.LIB: self.cxx_phase = self.__class__.InstallHeaders(self)
				for x in ModTask.__call__(self, sched_ctx): yield x
			
			def do_mod_phase(self):
				self.cfg.include_paths.appendleft(src_dir)
				if self.path.exists:
					for s in self.path.find_iter(in_pats = ('*.cpp',), prune_pats = ('todo',)): self.sources.append(s)
				else: self.sources.append(self.path.parent / (self.path.name + '.cpp'))

			def apply_cxx_to(self, cfg):
				if self.cxx_phase is not None and not self.cxx_phase.dest_dir in cfg.include_paths:
					cfg.include_paths.append(self.cxx_phase.dest_dir)
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
							for s in self.outer.path.find_iter(in_pats = ('*.hpp','*.h'),
								ex_pats = ('*.private.hpp',), prune_pats = ('todo',)): self._sources.append(s)
						for h in ('.hpp', '.h'):
							f = self.outer.path.parent / (self.outer.path.name + h)
							if f.exists:
								self._sources.append(f)
								break
						return self._sources

		n = 'psycle-plugin-'
		p = src_dir / 'psycle' / 'plugins'

		alk_muter = UniformMod(n + 'alk-muter', p / 'alk_muter')
		arguru_cross_delay = UniformMod(n + 'arguru-xfilter', p / 'arguru_xfilter')
		arguru_distortion = UniformMod(n + 'arguru-distortion', p / 'arguru_distortion')
		arguru_goaslicer = UniformMod(n + 'arguru-goaslicer', p / 'arguru_goaslicer')
		arguru_reverb = UniformMod(n + 'arguru-reverb', p / 'arguru_reverb')
		arguru_synth = UniformMod(n + 'arguru-synth-2f', p / 'arguru_synth_2_final')
		arguru_yezar_freeverb = UniformMod(n + 'arguru-freeverb', p / 'yezar_freeverb')
		audacity_compressor = UniformMod(n + 'audacity-compressor', p / 'audacity' / 'compressor')
		audacity_phaser = UniformMod(n + 'audacity-phaser', p / 'audacity' / 'phaser')
		audacity_wahwah = UniformMod(n + 'wahwah', p / 'audacity' / 'wahwah')
		ayeternal_2_pole_filter = UniformMod(n + 'filter-2-poles', p / 'filter_2_poles')
		ayeternal_delay = UniformMod(n + 'delay', p / 'delay')
		ayeternal_distortion = UniformMod(n + 'distortion', p / 'distortion')
		ayeternal_gainer = UniformMod(n + 'gainer', p / 'gainer')
		ayeternal_ring_modulator = UniformMod(n + 'ring-modulator', p / 'ring_modulator')
		bdzld_negative = UniformMod(n + 'negative', p / 'negative')
		docbexter_phaser = UniformMod(n + 'bexphase', p / 'bexphase')
		dw_granulizer = UniformMod(n + 'dw-granulizer', p / 'dw' / 'granulizer')
		dw_iopan = UniformMod(n + 'dw-iopan', p / 'dw' / 'iopan')
		dw_tremolo = UniformMod(n + 'dw-tremolo', p / 'dw' / 'tremolo')
		gzero_synth = UniformMod(n + 'gzero-synth', p / 'gzero_synth')
		haas = UniformMod(n + 'haas', p / 'haas')
		jme_blitz = UniformMod(n + 'blitz', p / 'jme' / 'blitz')
		jme_gamefx = UniformMod(n + 'gamefx', p / 'jme' / 'gamefx')
		josepma_drums = UniformMod(n + 'jmdrum', p / 'jm_drums')
		karlkox_surround = UniformMod(n + 'karlkox-surround', p / 'surround')
		ladspa_gverb = UniformMod(n + 'gverb', p / 'gverb')
		legasynth_303 = UniformMod(n + 'legasynth-303', p / 'legasynth')
		m3 = UniformMod(n + 'm3', p / 'm3')
		moreamp_eq = UniformMod(n + 'maeq', p / 'moreamp_eq')
		pooplog_autopan = UniformMod(n + 'pooplog-autopan', p / 'pooplog_autopan')
		pooplog_delay = UniformMod(n + 'pooplog-delay', p / 'pooplog_delay')
		pooplog_delay_light = UniformMod(n + 'pooplog-delay-light', p / 'pooplog_delay_light')
		pooplog_filter = UniformMod(n + 'pooplog-filter', p / 'pooplog_filter')
		pooplog_fm_laboratory = UniformMod(n + 'pooplog-fm-laboratory', p / 'pooplog_synth')
		pooplog_fm_light = UniformMod(n + 'pooplog-fm-light', p / 'pooplog_synth_light')
		pooplog_fm_ultralight = UniformMod(n + 'pooplog-fm-ultralight', p / 'pooplog_synth_ultralight')
		pooplog_lofi_processor = UniformMod(n + 'pooplog-lofi-processor', p / 'pooplog_lofi')
		pooplog_scratch_master = UniformMod(n + 'pooplog-scratch-master', p / 'pooplog_scratch')
		pooplog_scratch_master_2 = UniformMod(n + 'pooplog-scratch-master-2', p / 'pooplog_scratch_2')
		satorius_chorus = UniformMod(n + 'schorus', p / 'SChorus')
		thunderpalace_softsat = UniformMod(n + 'thunderpalace-softsat', p / 'graue' / 'softsat')
		vincenzo_demasi_all_pass = UniformMod(n + 'vdallpass', p / 'vincenzo_demasi' / 'vdAllPass')
		vincenzo_demasi_echo = UniformMod(n + 'vdecho', p / 'vincenzo_demasi' / 'vdEcho')
		vincenzo_demasi_fastverb = UniformMod(n + 'vsfastverb', p / 'vincenzo_demasi' / 'vsFastVerb')
		vincenzo_demasi_noise_gate = UniformMod(n + 'vdnoisegate', p / 'vincenzo_demasi' / 'vdNoiseGate')
		zephod_super_fm = UniformMod(n + 'zephod-superfm', p / 'zephod_super_fm')
		
		dw_filter = UniformMod('psycle-dw-filter', p / 'dw' / 'dw_filter', kind=ModTask.Kinds.LIB)
		dw_eq = UniformMod(n + 'dw-eq', p / 'dw' / 'eq', deps=(dw_filter,))
		
		druttis_band_limited_wave_tables = UniformMod('psycle-druttis-band-limited-wave-tables', p / 'druttis' / 'blwtbl')

		druttis_dsp = UniformMod('psycle-druttis-dsp', p / 'druttis' / 'dsp', kind=ModTask.Kinds.LIB,
			deps=(druttis_band_limited_wave_tables,))
			
		druttis_sublime = UniformMod(n + 'sublime', p / 'druttis' / 'sublime', deps=(druttis_dsp,))
		druttis_slicit = UniformMod(n + 'slicit', p / 'druttis' / 'slicit', deps=(druttis_dsp,))
		druttis_eq3 = UniformMod(n + 'eq3', p / 'druttis' / 'eq3', deps=(druttis_dsp,))

		druttis_dsp_class = UniformMod('psycle-druttis-dsp-class', p / 'druttis' / 'CDsp', kind=ModTask.Kinds.LIB,
			deps=(druttis_band_limited_wave_tables,))
			
		druttis_envelope_class = UniformMod('psycle-druttis-envelope-class', p / 'druttis' / 'CEnvelope', kind=ModTask.Kinds.LIB)

		druttis_feed_me = UniformMod(n + 'feedme', p / 'druttis' / 'FeedMe', deps=(druttis_dsp_class, druttis_envelope_class))
		
if False: # TODO clean the mess with druttis libs

	druttis_plucked_string = plugin_module('pluckedstring', 'druttis plucked string')
	druttis_plucked_string.add_plugin_sources([os.path.join('druttis', 'PluckedString', '*.cpp')])
	druttis_plucked_string.add_dependencies([druttis_lib])

	druttis_phantom = plugin_module('phantom', 'druttis phantom')
	druttis_phantom.add_plugin_sources([os.path.join('druttis', 'Phantom', '*.cpp')])
	druttis_phantom.add_dependencies([druttis_dsp_class, druttis_envelope_class, druttis_dsp_lib])

	druttis_koruz = plugin_module('koruz', 'druttis koruz')
	druttis_koruz.add_plugin_sources([os.path.join('druttis', 'Koruz', '*.cpp')])
	druttis_koruz.add_dependencies([druttis_dsp_class, druttis_dsp_lib])

	druttis_lib_module = module(source_package,
		name = 'druttis_lib',
		version = source_package.version(),
		description = 'druttis lib',
		dependencies = [universalis] # note this is actually a dependency on psycle-helpers
	)
	druttis_lib_module.add_sources(find(project, 'src', [os.path.join('psycle', 'plugins', 'druttis', 'Lib', file) for file in (
		'BiQuad.cpp', 'CEnvelope.cpp', 'DLineN.cpp')]))
	druttis_lib_module.add_headers(find(project, 'src', [os.path.join('psycle', 'plugins', 'druttis', 'Lib', file) for file in (
		'BiQuad.h', 'CEnvelope.h', 'DLineN.h')]))
	druttis_lib_package = pkg_config_package(project,
		name = 'druttis-lib-' + str(druttis_lib_module.version().major()),
		version = druttis_lib_module.version(),
		description = druttis_lib_module.description(),
		modules = [druttis_lib_module]
	)
	druttis_lib = druttis_lib_package.local_package()

	druttis_dsp_lib_module = module(source_package,
		name = 'druttis_dsp_lib',
		version = source_package.version(),
		description = 'druttis dsp lib',
		dependencies = []
	)
	#druttis_dsp_lib_module.add_sources(find(project, 'src', [os.path.join('psycle', 'plugins', 'druttis', 'DspLib', 'AllPass.cpp')]))
	druttis_dsp_lib_module.add_headers(find(project, 'src', [os.path.join('psycle', 'plugins', 'druttis', 'DspLib', 'AllPass.h')]))
	druttis_dsp_lib_module.add_sources(find(project, 'src', [os.path.join('psycle', 'plugins', 'druttis', 'Lib', 'DspAlgs.cpp')])) # todo header is lowercase while source is not
	druttis_dsp_lib_module.add_headers(find(project, 'src', [os.path.join('psycle', 'plugins', 'druttis', 'Lib', 'dspalgs.h')]))
	druttis_dsp_lib_package = pkg_config_package(project,
		name = 'druttis-dsp-lib-' + str(druttis_dsp_lib_module.version().major()),
		version = druttis_dsp_lib_module.version(),
		description = druttis_dsp_lib_module.description(),
		modules = [druttis_dsp_lib_module]
	)
	druttis_dsp_lib = druttis_dsp_lib_package.local_package()

	if False: # it uses the msapi!
		plugin_module('ymidi', 'yannis brown midi').add_plugin_sources([os.path.join('y_midi', '*.cpp')])

	if False: # [bohan] i haven't found this one listed in the closed-source dir, but i can't find its sources either!
		plugin_module('guido_volume', 'guido volume').add_plugin_sources(['?????!!!!!!!!'])
	
	from sconscrap.std_checks.dlfcn import dlfcn
	dlfcn = dlfcn(project)
	if dlfcn.result():
		# whoops, it uses the posix api!
		# I have to rewrite it using glibmm.
		# -- bohan
		class plugin_check_module(module):
			def __init__(self):
				module.__init__(self, source_package,
					name = 'psycle-plugin-check',
					version = source_package.version(),
					description = 'psycle plugin sanity check',
					dependencies = [universalis, dlfcn],
					target_type = module.target_types.program
				)
				modules.append(self)
			def dynamic_dependencies(self):
				self.add_sources(find(project, 'src', [os.path.join('psycle', 'plugin_check.cpp')]))
		plugin_check_module = plugin_check_module()
