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

		universalis = ScriptLoaderTask.shared(project, top_src_dir / 'universalis')
		helpers = ScriptLoaderTask.shared(project, top_src_dir / 'psycle-helpers')
		for x in sched_ctx.parallel_wait(universalis, helpers): yield x
		universalis = universalis.script_task
		self._common = common = universalis.common
		universalis = universalis.mod_dep_phases
		helpers_math = helpers.script_task.math_mod_dep_phases
		pch = common.pch
		cfg = common.cfg.new_or_clone()

		from wonderbuild import UserReadableException
		from wonderbuild.cxx_tool_chain import PkgConfigCheckTask, ModTask
		from wonderbuild.std_checks.dsound import DSoundCheckTask
		from wonderbuild.install import InstallTask

		check_cfg = cfg.clone()
		gstreamer = PkgConfigCheckTask.shared(check_cfg, ['gstreamer-0.10 >= 0.10', 'gstreamer-plugins-base-0.10 >= 0.10'])
		jack = PkgConfigCheckTask.shared(check_cfg, ['jack >= 0.101.1'])
		alsa = PkgConfigCheckTask.shared(check_cfg, ['alsa >= 1.0'])
		gtkmm = PkgConfigCheckTask.shared(check_cfg, ['gtkmm-2.4 >= 2.4'])
		gnomecanvasmm = PkgConfigCheckTask.shared(check_cfg, ['libgnomecanvasmm-2.6 >= 2.6'])
		cluttermm = PkgConfigCheckTask.shared(check_cfg, ['clutter-0.6 >= 0.6'])
		dsound = DSoundCheckTask.shared(check_cfg)

		for x in sched_ctx.parallel_wait(gstreamer, jack, alsa, dsound, gtkmm, gnomecanvasmm, cluttermm): yield x

		class UniformMod(ModTask):
			def __init__(self, name, path, deps=None, kind=ModTask.Kinds.LOADABLE):
				ModTask.__init__(self, name, kind, cfg, (name, 'default'))
				self.path = path
				if deps is not None: self.public_deps += deps

			def __call__(self, sched_ctx):
				if self.kind == ModTask.Kinds.PROG: self.private_deps = [pch.prog_task]
				else: self.private_deps = [pch.lib_task]
				self.public_deps += [universalis, helpers_math]
				req = self.all_deps
				for x in sched_ctx.parallel_wait(*req): yield x
				self.result = min(bool(r) for r in req)
				self.cxx_phase = self.__class__.InstallHeaders(self)
				for x in ModTask.__call__(self, sched_ctx): yield x
			
			def do_mod_phase(self):
				self.cfg.include_paths.appendleft(src_dir)
				self.cfg.defines['UNIVERSALIS__META__PACKAGE__NAME'] = '"freepsycle"'
				self.cfg.defines['UNIVERSALIS__META__PACKAGE__VERSION'] = 0
				self.cfg.defines['UNIVERSALIS__META__MODULE__NAME'] = '"' + self.name +'"'
				self.cfg.defines['UNIVERSALIS__META__MODULE__VERSION'] = 0
				if self.path.exists:
					for s in self.path.find_iter(in_pats = ('*.cpp',), prune_pats = ('todo',)): self.sources.append(s)
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
								in_pats = ('*.hpp',), ex_pats = ('*.private.hpp',), prune_pats = ('todo',)): self._sources.append(s)
						f = self.outer.path.parent / (self.outer.path.name + '.hpp')
						if f.exists: self._sources.append(f)
						return self._sources

		paths = UniformMod('freepsycle-path', src_dir / 'psycle' / 'paths', kind=ModTask.Kinds.LIB)
		engine = UniformMod('freepsycle-engine', src_dir / 'psycle' / 'engine', kind=ModTask.Kinds.LIB)
		host = UniformMod('freepsycle-host', src_dir / 'psycle' / 'host', deps=(engine,), kind=ModTask.Kinds.LIB)
		stream = UniformMod('freepsycle-stream', src_dir / 'psycle' / 'stream', kind=ModTask.Kinds.LIB)
		resource = UniformMod('freepsycle-plugin-resource', src_dir / 'psycle' / 'plugins' / 'resource', deps=(engine,), kind=ModTask.Kinds.LIB)
		decay = UniformMod('freepsycle-plugin-decay', src_dir / 'psycle' / 'plugins' / 'decay', deps=(engine,))
		sequence = UniformMod('freepsycle-plugin-sequence', src_dir / 'psycle' / 'plugins' / 'sequence', deps=(engine,))
		sine = UniformMod('freepsycle-plugin-sine', src_dir / 'psycle' / 'plugins' / 'sine', deps=(engine,))
		bipolar_filter = UniformMod('freepsycle-plugin-bipolar-filter', src_dir / 'psycle' / 'plugins' / 'bipolar_filter', deps=(engine,))
		additioner = UniformMod('freepsycle-plugin-additioner', src_dir / 'psycle' / 'plugins' / 'additioner', deps=(bipolar_filter,))
		multiplier = UniformMod('freepsycle-plugin-multiplier', src_dir / 'psycle' / 'plugins' / 'multiplier', deps=(bipolar_filter,))

		default_output_impl = None
		
		if dsound:
			dsound_output = UniformMod('freepsycle-plugin-output-direct-sound',
				src_dir / 'psycle' / 'plugins' / 'outputs' / 'direct_sound',
				deps=(resource, stream, dsound))
			if default_output_impl is None: default_output_impl = dsound_output

		if gstreamer:
			gst_output = UniformMod('freepsycle-plugin-output-gstreamer',
				src_dir / 'psycle' / 'plugins' / 'outputs' / 'gstreamer',
				deps=(resource, stream, gstreamer))
			if default_output_impl is None: default_output_impl = gst_output

		if alsa:
			alsa_output = UniformMod('freepsycle-plugin-output-alsa',
				src_dir / 'psycle' / 'plugins' / 'outputs' / 'alsa',
				deps=(resource, stream, alsa))
			if default_output_impl is None: default_output_impl = alsa_output

		if jack:
			jack_output = UniformMod('freepsycle-plugin-output-jack',
				src_dir / 'psycle' / 'plugins' / 'outputs' / 'jack',
				deps=(resource, stream, jack))
			if default_output_impl is None: default_output_impl = jack_output

		dummy_output = UniformMod('freepsycle-plugin-output-dummy',
			src_dir / 'psycle' / 'plugins' / 'outputs' / 'dummy',
			deps=(resource,))
		if default_output_impl is None: default_output_impl = dummy_output

		#print 'selected ' + default_output_impl.name + ' as default output plugin module.'
		class DefaultOutput(UniformMod):
			def __init__(self): UniformMod.__init__(self, 'freepsycle-plugin-output',
				src_dir / 'psycle' / 'plugins' / 'output',
				deps=(default_output_impl,))

			def apply_defines_to(self, cfg):
				cfg.defines['PSYCLE__PLUGINS__OUTPUT__DEFAULT__' + default_output_impl.path.name.replace('-', '_').upper()] = None

			def do_mod_phase(self):
				self.apply_defines_to(self.cfg)
				UniformMod.do_mod_phase(self)
				
			def apply_cxx_to(self, cfg): self.apply_defines_to(cfg)

		default_output = DefaultOutput()

		random_notes = UniformMod('freepsycle-test-random-notes',
			src_dir / 'psycle' / 'tests' / 'random_notes',
			deps=(host, paths, default_output, sequence, decay, additioner, sine), kind=ModTask.Kinds.PROG)

		if gtkmm and gnomecanvasmm and cluttermm:
			gui = UniformMod('freepsycle-gui',
				src_dir / 'psycle' / 'front_ends' / 'gui',
				deps=(host, paths, gtkmm, gnomecanvasmm, cluttermm), kind=ModTask.Kinds.PROG)
