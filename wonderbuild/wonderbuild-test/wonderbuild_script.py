#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

def wonderbuild_script(project):
	from wonderbuild.cxx_chain import UserCfg, PkgCfg, DevCfg, ModTask

	user_cfg = UserCfg(project)

	src_dir = project.src_node.node_path('src')

	if False:	
		class PCH(CxxPCH):
			def sources(self):
				try: return self._sources
				except AttributeError:
					for s in src_dir.find_iter(in_pats = ['*.hpp'], prune_pats = ['todo']): self._sources.append(s)
					return self._sources
		pch = PCH(project)

	class LibFoo(ModTask):
		def __init__(self): ModTask.__init__(self, LibFoo.Cfg(user_cfg, 'lib'), 'foo')

		class Cfg(DevCfg):
			def configure(self):
				DevCfg.configure(self)
				##pkg_cfg = PkgCfg(self.project)
				##pkg_cfg.pkgs = ['glibmm-2.4']
				##self.pkgs = [pkg_cfg]
				#if pkg_cfg.exists: self.pkgs += pkg_cfg.pkgs

		def dyn_in_tasks(self, sched_ctx):
			self.cfg.include_paths = [src_dir]
			for s in src_dir.node_path('foo').find_iter(in_pats = ['*.cpp'], prune_pats = ['todo']): self.sources.append(s)
			return ModTask.dyn_in_tasks(self, sched_ctx)
	lib_foo = LibFoo()

	class MainProg(ModTask):
		def __init__(self): ModTask.__init__(self, MainProg.Cfg(user_cfg, 'prog'), 'main')

		class Cfg(DevCfg):
			def configure(self):
				DevCfg.configure(self)
				self.include_paths = [src_dir]
				self.libs_paths.append(lib_foo.target.parent)
				self.libs.append(lib_foo.name)

		def dyn_in_tasks(self, sched_ctx):
			self.add_in_task(lib_foo)
			for s in src_dir.node_path('main').find_iter(in_pats = ['*.cpp'], prune_pats = ['todo']): self.sources.append(s)
			return ModTask.dyn_in_tasks(self, sched_ctx)
	main_prog = MainProg()

	return [main_prog]
