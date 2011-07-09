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

	def __call__(self, sched_ctx):
		project = self.project
		top_src_dir = self.src_dir.parent
		src_dir = self.src_dir / 'src'
		default_tasks = self.default_tasks

		universalis = ScriptLoaderTask.shared(project, top_src_dir / 'universalis')
		helpers = ScriptLoaderTask.shared(project, top_src_dir / 'psycle-helpers')
		for x in sched_ctx.parallel_wait(universalis, helpers): yield x
		universalis = universalis.script_task
		helpers = helpers.script_task
		self._common = common = universalis.common
		universalis = universalis.mod_dep_phases
		helpers_math = helpers.math_mod_dep_phases
		helpers = helpers.mod_dep_phases
		pch = common.pch
		cfg = common.cfg.clone()

		from wonderbuild import UserReadableException
		from wonderbuild.cxx_tool_chain import ModTask, BuildCheckTask
		from wonderbuild.install import InstallTask

		check_cfg = cfg.clone()

		class StkCheckTask(BuildCheckTask):
			@staticmethod
			def shared_uid(*args, **kw): return 'stk'

			def apply_to(self, cfg): cfg.libs.extend(['stk'])#, 'asound', 'jack']) # stk uses alsa and jack!

			@property
			def source_text(self): return '#include <stk/Stk.h>'
		stk = StkCheckTask.shared(check_cfg)

		class UniformMod(ModTask):
			def __init__(self, name, path, deps=None, kind=ModTask.Kinds.LOADABLE):
				ModTask.__init__(self, name, kind, cfg)
				self.path = path
				if deps is not None: self.public_deps += deps
				if kind in (ModTask.Kinds.PROG, ModTask.Kinds.LOADABLE): default_tasks.append(self.mod_phase)

			def __call__(self, sched_ctx):
				if self.kind == ModTask.Kinds.PROG: self.private_deps = [pch.prog_task]
				else: self.private_deps = [pch.lib_task]
				self.public_deps += [universalis, helpers_math, helpers]
				req = self.all_deps
				for x in sched_ctx.parallel_wait(*req): yield x
				self.result = min(bool(r) for r in req)
				if self.kind == ModTask.Kinds.LIB: self.cxx_phase = self.__class__.InstallHeaders(self)
			
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
							for s in self.outer.path.find_iter(in_pats = ('*.hpp', '*.h'),
								ex_pats = ('*.private.hpp',), prune_pats = ('todo',)): self._sources.append(s)
						for h in ('.hpp', '.h'):
							f = self.outer.path.parent / (self.outer.path.name + h)
							if f.exists:
								self._sources.append(f)
								break
						return self._sources
						
			def apply_cxx_to(self, cfg):
				if self.cxx_phase is not None and not self.cxx_phase.dest_dir in cfg.include_paths:
					cfg.include_paths.append(self.cxx_phase.dest_dir)

			def do_mod_phase(self):
				self.cfg.include_paths.appendleft(src_dir)
				self.cfg.defines['UNIVERSALIS__META__MODULE__NAME'] = '"' + self.name +'"'
				self.cfg.defines['UNIVERSALIS__META__MODULE__VERSION'] = 0
				if self.path.exists:
					for s in self.path.find_iter(in_pats = ('*.cpp',), prune_pats = ('todo',)): self.sources.append(s)
				else: self.sources.append(self.path.parent / (self.path.name + '.cpp'))

		n = 'psycle-plugin-'
		p = src_dir / 'psycle' / 'plugins'

		alk_muter = UniformMod(n + 'alk-muter', p / 'alk_muter')
		arguru_cross_delay = UniformMod(n + 'arguru-xfilter', p / 'arguru_xfilter')
		arguru_distortion = UniformMod(n + 'arguru-distortion', p / 'arguru_distortion')
		arguru_goaslicer = UniformMod(n + 'arguru-goaslicer', p / 'arguru_goaslicer')
		arguru_reverb = UniformMod(n + 'arguru-reverb', p / 'arguru_reverb')
		arguru_synth = UniformMod(n + 'arguru-synth-2f', p / 'arguru_synth_2_final')
		arguru_yezar_freeverb = UniformMod(n + 'arguru-freeverb', p / 'yezar_freeverb')
		arguru_compressor = UniformMod(n + 'arguru-compressor', p / 'arguru_compressor')
		audacity_compressor = UniformMod(n + 'audacity-compressor', p / 'audacity' / 'compressor')
		audacity_phaser = UniformMod(n + 'audacity-phaser', p / 'audacity' / 'phaser')
		audacity_wahwah = UniformMod(n + 'wahwah', p / 'audacity' / 'wahwah')
		ayeternal_2_pole_filter = UniformMod(n + 'filter-2-poles', p / 'filter_2_poles')
		ayeternal_delay = UniformMod(n + 'delay', p / 'delay')
		ayeternal_distortion = UniformMod(n + 'distortion', p / 'distortion')
		ayeternal_flanger = UniformMod(n + 'flanger', p / 'flanger')
		ayeternal_gainer = UniformMod(n + 'gainer', p / 'gainer')
		ayeternal_ring_modulator = UniformMod(n + 'ring-modulator', p / 'ring_modulator')
		bdzld_negative = UniformMod(n + 'negative', p / 'negative')
		docbexter_phaser = UniformMod(n + 'bexphase', p / 'bexphase')
		crasher = UniformMod(n + 'crasher', p / 'crasher')
		dw_granulizer = UniformMod(n + 'dw-granulizer', p / 'dw' / 'granulizer')
		dw_iopan = UniformMod(n + 'dw-iopan', p / 'dw' / 'iopan')
		dw_tremolo = UniformMod(n + 'dw-tremolo', p / 'dw' / 'tremolo')
		gzero_synth = UniformMod(n + 'gzero-synth', p / 'gzero_synth')
		haas = UniformMod(n + 'haas', p / 'haas')
		jme_blitz = UniformMod(n + 'blitz', p / 'jme' / 'blitz')
		jme_gamefx = UniformMod(n + 'gamefx', p / 'jme' / 'gamefx')
		josepma_drums = UniformMod(n + 'jmdrum', p / 'jm_drums')
		karlkox_surround = UniformMod(n + 'karlkox-surround', p / 'surround')
		ladspa_gverb = UniformMod(n + 'ladspa-gverb', p / 'gverb')
		legasynth_303 = UniformMod(n + 'legasynth-303', p / 'legasynth')
		m3 = UniformMod(n + 'm3', p / 'm3')
		moreamp_eq = UniformMod(n + 'maeq', p / 'moreamp_eq')
		nrs_7900_fractal = UniformMod(n + 'nrs-7900-fractal', p / 'ninereeds_7900')
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
		
		druttis_dsp = UniformMod('psycle-druttis-dsp', p / 'druttis' / 'dsp', kind=ModTask.Kinds.LIB)
		druttis_band_limited_wave_tables = UniformMod('psycle-druttis-band-limited-wave-tables', p / 'druttis' / 'blwtbl', 
			deps=(druttis_dsp,))
			
		druttis_plucked_string = UniformMod(n + 'pluckedstring', p / 'druttis' / 'PluckedString',
			deps=(druttis_dsp,))

		druttis_sublime = UniformMod(n + 'sublime', p / 'druttis' / 'sublime', 
			deps=(druttis_dsp,druttis_band_limited_wave_tables))

		druttis_slicit = UniformMod(n + 'slicit', p / 'druttis' / 'slicit', deps=(druttis_dsp,))
		druttis_eq3 = UniformMod(n + 'eq3', p / 'druttis' / 'eq3', deps=(druttis_dsp,))
		druttis_koruz = UniformMod(n + 'koruz', p / 'druttis' / 'Koruz',
			deps=(druttis_dsp,))

		druttis_phantom = UniformMod(n + 'phantom', p / 'druttis' / 'Phantom',
			deps=(druttis_dsp,))

		druttis_feed_me = UniformMod(n + 'feedme', p / 'druttis' / 'FeedMe',
			deps=(druttis_dsp,))

		if False: # it uses ms's winapi!
			yannis_brown_midi = UniformMod(n + 'ymidi', p / 'y_midi')

		if False: # [bohan] i haven't found this one listed in the closed-source dir, but i can't find its sources either!
			guido_volume = UniformMod(n + 'guido-volume', p / '?????!!!!!!!!')
		
		for x in sched_ctx.parallel_wait(stk): yield x

		if stk:
			stk_plucked = UniformMod(n + 'stk-plucked', p / 'stk' / 'stk.plucked', deps=(stk,))
			stk_rev = UniformMod(n + 'stk-rev', p / 'stk' / 'stk.reverbs', deps=(stk,))
			stk_shakers = UniformMod(n + 'stk-shakers', p / 'stk' / 'stk.shakers', deps=(stk,))
