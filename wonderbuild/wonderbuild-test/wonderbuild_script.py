#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

def wonderbuild_script(project):
	from wonderbuild.cxx_chain import BaseCxxCfg, BaseModCfg, PkgCfg, CxxCfg, ModCfg, ModTask

	base_cxx_cfg = BaseCxxCfg(project)
	base_mod_cfg = BaseModCfg(base_cxx_cfg)

	class LibFoo(ModTask):
		def __init__(self): ModTask.__init__(self, ModCfg(base_mod_cfg, LibFoo.FooCxxCfg(base_cxx_cfg), 'lib'), 'foo')

		def dyn_in_tasks(self):
			src_dir = self.project.src_node.node_path('src')
			self.cxx_cfg.paths = [src_dir]
			for s in src_dir.node_path('foo').find_iter(prunes = ['todo'], in_pat = '*.cpp'): self.add_new_cxx_task(s)
			#for h in src_dir.node_path('foo').find_iter(prunes = ['todo'], in_pat = '*.hpp', ex_pat = '*.private.hpp'): print h.path
			return self.in_tasks

		class FooCxxCfg(CxxCfg):
			def configure(self):
				CxxCfg.configure(self)
				pkg_cfg = PkgCfg(self.project)
				pkg_cfg.pkgs = ['glibmm-2.4']
				self.pkgs = [pkg_cfg]
				#if pkg_cfg.exists: self.pkgs += pkg_cfg.pkgs
	lib_foo = LibFoo()

	class MainProg(ModTask):
		def __init__(self): ModTask.__init__(self, MainProg.MainModCfg(base_mod_cfg, CxxCfg(base_cxx_cfg), 'prog'), 'main')

		class MainModCfg(ModCfg):
			def configure(self):
				ModCfg.configure(self)
				self.paths.append(lib_foo.target.parent)
				self.libs.append(lib_foo.name)

		def dyn_in_tasks(self):
			self.add_in_task(lib_foo)
			src_dir = self.project.src_node.node_path('src')
			self.cxx_cfg.paths = [src_dir]
			for s in src_dir.node_path('main').find_iter(prunes = ['todo'], in_pat = '*.cpp'): self.add_new_cxx_task(s)
			#for h in src_dir.node_path('foo').find_iter(prunes = ['todo'], in_pat = '*.hpp', ex_pat = '*.private.hpp'): print h.path
			return self.in_tasks
	main_prog = MainProg()

	return [main_prog]
