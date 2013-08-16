#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2009-2013 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

if __name__ == '__main__':
	import sys, os
	dir = os.path.dirname(__file__)
	sys.argv.append('--src-dir=' + dir)
	try: from wonderbuild.main import main
	except ImportError:
		dir = os.path.abspath(os.path.join(dir, os.pardir, os.pardir))
		if dir not in sys.path: sys.path.append(dir)
		try: from wonderbuild.main import main
		except ImportError:
			print >> sys.stderr, 'could not find wonderbuild'
			sys.exit(1)
		else: main()
	else: main()

else:
	from wonderbuild.script import ScriptTask

	class Wonderbuild(ScriptTask):
		def __call__(self, sched_ctx):
			from wonderbuild.cxx_tool_chain import UserBuildCfgTask, ModTask
			from wonderbuild.install import InstallTask

			test_name = self.src_dir.name
			src_dir = self.src_dir / 'src'

			cfg = UserBuildCfgTask.shared(self.project)
			for x in sched_ctx.parallel_wait(cfg): yield x
			cfg = cfg.clone()
			if not src_dir in cfg.include_paths: cfg.include_paths.append(src_dir)
			
			cfg.shared = True
			cfg.static_prog = False
			static_cfg = cfg.clone()
			static_cfg.shared = False
			static_cfg.static_prog = True

			def variant(static_prog, static_wrapper, static_impl):
				static_cfg.pic = False
				if static_impl and not static_wrapper: static_cfg.pic = True

				
				variant_name = \
					(static_prog and 'st' or 'sh') + '-' + \
					(static_wrapper and 'st' or 'sh') + '-' + \
					(static_impl and 'st' or 'sh')

				# dependencies: MainProg ---public---> LibThickWrapper ---private---> LibImpl

				class LibImpl(ModTask):
					def __init__(self): ModTask.__init__(self,
						test_name + '--' + variant_name + '--impl',
						ModTask.Kinds.LIB, static_impl and static_cfg or cfg,
						# some random version information, just for more fun
						version_interface=4, version_interface_min=2, version_impl=10, version_string='4:2:10')

					def __call__(self, sched_ctx):
						self.result = True
						self.cxx_phase = self.__class__.Install(self.cfg.project, self.name + '-headers')
						if False: yield

					def do_mod_phase(self):
						self.cfg.defines['IMPL'] = self.cfg.shared and '1' or '-1'
						for s in (src_dir / 'impl').find_iter(('*.cpp',)): self.sources.append(s)

					def apply_cxx_to(self, cfg):
						if not self.cxx_phase.dest_dir in cfg.include_paths: cfg.include_paths.append(self.cxx_phase.dest_dir)
						if not self.cfg.shared: cfg.defines['IMPL'] = '-1'
					
					class Install(InstallTask):
						@property
						def trim_prefix(self): return src_dir

						@property
						def sources(self):
							try: return self._sources
							except AttributeError:
								self._sources = []
								for s in (self.trim_prefix / 'impl').find_iter(('*.hpp',)): self._sources.append(s)
								return self._sources
	
						@property
						def dest_dir(self): return self.fhs.include / test_name / variant_name
				lib_impl = LibImpl()

				class LibThickWrapper(ModTask):
					def __init__(self): ModTask.__init__(self,
						test_name + '--' + variant_name + '--wrapper',
						ModTask.Kinds.LIB, static_wrapper and static_cfg or cfg,
						# some random version information, just for more fun
						version_interface=2, version_interface_min=1, version_impl=5, version_string='2:1:5')

					def __call__(self, sched_ctx):
						if True: # thick wrapper: dependency in the translation unit's main source file
							self.private_deps = [lib_impl]
						else: # thin wrapper: dependency in the public header file
							self.public_deps = [lib_impl]
						self.result = True
						self.cxx_phase = self.__class__.Install(self.cfg.project, self.name + '-headers')
						for x in sched_ctx.parallel_wait(lib_impl): yield x # XXX listing them as a deps should suffice.

					def do_mod_phase(self):
						self.cfg.defines['WRAPPER'] = self.cfg.shared and '1' or '-1'
						for s in (src_dir / 'wrapper').find_iter(('*.cpp',)): self.sources.append(s)

					def apply_cxx_to(self, cfg):
						if not self.cxx_phase.dest_dir in cfg.include_paths: cfg.include_paths.append(self.cxx_phase.dest_dir)
						if not self.cfg.shared: cfg.defines['WRAPPER'] = '-1'

					class Install(InstallTask):
						@property
						def trim_prefix(self): return src_dir

						@property
						def sources(self):
							try: return self._sources
							except AttributeError:
								self._sources = []
								for s in (self.trim_prefix / 'wrapper').find_iter(('*.hpp',)): self._sources.append(s)
								return self._sources
	
						@property
						def dest_dir(self): return self.fhs.include / test_name / variant_name
				lib_thick_wrapper = LibThickWrapper()

				class MainProg(ModTask):
					def __init__(self): ModTask.__init__(self,
						test_name + '--' + variant_name + '--main',
						ModTask.Kinds.PROG, static_prog and static_cfg or cfg)

					def __call__(self, sched_ctx):
						self.public_deps = [lib_thick_wrapper]#, lib_thin_wrapper]
						for x in sched_ctx.parallel_wait(*self.public_deps): yield x # XXX listing them as deps should suffice.
			
					def do_mod_phase(self):
						for s in (src_dir / 'main').find_iter(('*.cpp',)): self.sources.append(s)
				main_prog = MainProg()
				self.default_tasks.append(main_prog.mod_phase)
				
			variant(True, True, True)
			variant(False, True, True)
			variant(False, True, False)
			variant(False, False, False)
			variant(False, False, True)
