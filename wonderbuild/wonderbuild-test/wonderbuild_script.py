#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

def wonderbuild_script(project):
	from cxx_chain import BaseObjConf, BaseModConf
	base_obj_conf = BaseObjConf(project)
	base_mod_conf = BaseModConf(base_obj_conf)

	from cxx_chain import PkgConf, ObjConf, ModConf, Mod

	class LibFoo(Mod):
		def __init__(self): Mod.__init__(self, ModConf(base_mod_conf, LibFoo.FooObjConf(base_obj_conf), 'lib'), 'foo')

		def dyn_in_tasks(self):
			if len(self.in_tasks) != 0: return None
			Mod.dyn_in_tasks(self)
			src_dir = self.project.src_node.node_path('src')
			self.obj_conf.paths = [src_dir]
			for s in src_dir.node_path('foo').find_iter(prunes = ['todo'], in_pat = '*.cpp'): self.new_obj(s)
			#for h in src_dir.node_path('foo').find_iter(prunes = ['todo'], in_pat = '*.hpp', ex_pat = '*.private.hpp'): print h.path
			return self.in_tasks

		class FooObjConf(ObjConf):
			def conf(self):
				ObjConf.conf(self)
				pkg_conf = PkgConf(self.project)
				pkg_conf.pkgs = ['glibmm-2.4']
				self.pkgs = [pkg_conf]
				#if pkg_conf.exists: self.pkgs += pkg_conf.pkgs
	lib_foo = LibFoo()

	class MainProg(Mod):
		def __init__(self): Mod.__init__(self, MainProg.MainModConf(base_mod_conf, ObjConf(base_obj_conf), 'prog'), 'main')

		class MainModConf(ModConf):
			def conf(self):
				ModConf.conf(self)
				self.paths.append(lib_foo.target.parent)
				self.libs.append(lib_foo.name)

		def dyn_in_tasks(self):
			try: self._dyn_in_tasks
			except AttributeError:
				self._dyn_in_tasks = None
				Mod.dyn_in_tasks(self)
				self.add_in_task(lib_foo)
				src_dir = self.project.src_node.node_path('src')
				self.obj_conf.paths = [src_dir]
				for s in src_dir.node_path('main').find_iter(prunes = ['todo'], in_pat = '*.cpp'): self.new_obj(s)
				#for h in src_dir.node_path('foo').find_iter(prunes = ['todo'], in_pat = '*.hpp', ex_pat = '*.private.hpp'): print h.path
				return self.in_tasks
	main_prog = MainProg()

	return [main_prog]
