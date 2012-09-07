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
		top_src_dir = self.src_dir.parent
		src_dir = self.src_dir / 'src'

		audiodrivers = ScriptLoaderTask.shared(self.project, top_src_dir / 'psycle-audiodrivers')
		for x in sched_ctx.parallel_wait(audiodrivers): yield x
		audiodrivers = audiodrivers.script_task
		self._common = common = audiodrivers.common
		audiodrivers = audiodrivers.mod_dep_phases
		pch = common.pch
		cfg = common.cfg.clone()

		from wonderbuild.cxx_tool_chain import PkgConfigCheckTask, ModTask
		from wonderbuild.std_checks.zlib import ZLibCheckTask
		from wonderbuild.install import InstallTask

		check_cfg = cfg.clone()
		xml = PkgConfigCheckTask.shared(check_cfg, ['libxml++-2.6'])
		zlib = ZLibCheckTask.shared(check_cfg)

		class CoreMod(ModTask):
			def __init__(self): ModTask.__init__(self, 'psycle-core', ModTask.Kinds.LIB, cfg)

			def __call__(self, sched_ctx):
				self.private_deps = [pch.lib_task]
				self.public_deps = [audiodrivers, zlib]
				req = self.public_deps + self.private_deps
				opt = [xml]
				for x in sched_ctx.parallel_wait(*(req + opt)): yield x
				self.public_deps += [o for o in opt if o]
				self.result = min(bool(r) for r in req)
				self.cxx_phase = CoreMod.InstallHeaders(self.base_cfg.project, self.name + '-headers')
			
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

			def _apply_defines_to(self, cfg):
				if xml: cfg.defines['PSYCLE__CORE__CONFIG__LIBXMLPP_AVAILABLE'] = None

			def apply_cxx_to(self, cfg):
				self._apply_defines_to(cfg)
				if not self.cxx_phase.dest_dir in cfg.include_paths: cfg.include_paths.append(self.cxx_phase.dest_dir)

			def do_mod_phase(self):
				self._apply_defines_to(self.cfg)
				self.cfg.defines['UNIVERSALIS__META__MODULE__NAME'] = '"' + self.name +'"'
				self.cfg.defines['UNIVERSALIS__META__MODULE__VERSION'] = 0
				self.cfg.include_paths.appendleft(src_dir)
				self.cfg.include_paths.appendleft(top_src_dir / 'psycle-plugins' / 'src')
				self.cfg.include_paths.appendleft(top_src_dir / 'external-packages' / 'vst-2.4')
				for s in (src_dir / 'psycle' / 'core').find_iter(
					in_pats = ('*.cpp',), prune_pats = ('todo',)
				): self.sources.append(s)
				for s in (src_dir / 'seib' / 'vst').find_iter(
					in_pats = ('*,coo',), prune_pats = ('todo',)
				): self.sources.append(s);

		self._mod_dep_phases = mod_dep_phases = CoreMod()
		self.default_tasks.append(mod_dep_phases.mod_phase)
