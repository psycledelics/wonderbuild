#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

def wonderbuild_script(project):
	from wonderbuild.cxx_chain import UserCfg, PkgCfg, DevCfg, ModTask

	user_cfg = UserCfg(project)

	src_dir = project.src_node.node_path('src')

	class LibFoo(ModTask):
		def __init__(self): ModTask.__init__(self, LibFoo.Cfg(user_cfg, 'lib'), 'foo')

		class Cfg(DevCfg):
			def configure(self):
				DevCfg.configure(self)
				##pkg_cfg = PkgCfg(self.project)
				##pkg_cfg.pkgs = ['glibmm-2.4']
				##self.pkgs = [pkg_cfg]
				#if pkg_cfg.exists: self.pkgs += pkg_cfg.pkgs

		def dyn(self):
			self.cxx_cfg.paths = [src_dir]
			for s in src_dir.node_path('foo').find_iter(prunes = ['todo'], in_pat = '*.cpp'): self.add_source(s)

		def dyn_in_tasks(self):
			self.cfg.include_paths = [src_dir]
			for s in src_dir.node_path('foo').find_iter(prunes = ['todo'], in_pat = '*.cpp'): self.add_new_cxx_task(s)
			#for h in src_dir.node_path('foo').find_iter(prunes = ['todo'], in_pat = '*.hpp', ex_pat = '*.private.hpp'): print h.path
			return self.in_tasks
	lib_foo = LibFoo()

	class MainProg(ModTask):
		def __init__(self): ModTask.__init__(self, MainProg.Cfg(user_cfg, 'prog'), 'main')

		class Cfg(DevCfg):
			def configure(self):
				DevCfg.configure(self)
				self.include_paths = [src_dir]
				self.libs_paths.append(lib_foo.target.parent)
				self.libs.append(lib_foo.name)

		def dyn_in_tasks(self):
			self.add_in_task(lib_foo)
			for s in src_dir.node_path('main').find_iter(prunes = ['todo'], in_pat = '*.cpp'): self.add_new_cxx_task(s)
			#for h in src_dir.node_path('foo').find_iter(prunes = ['todo'], in_pat = '*.hpp', ex_pat = '*.private.hpp'): print h.path
			return self.in_tasks
	main_prog = MainProg()

	return [main_prog]
