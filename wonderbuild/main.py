#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

def main():
	import sys, os

	from project import Project
	project = Project()

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
		def __init__(self):
			Mod.__init__(self, MainProg.MainModConf(base_mod_conf, ObjConf(base_obj_conf), 'prog'), 'main')
			self.add_in_task(lib_foo)

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
				src_dir = self.project.src_node.node_path('src')
				self.obj_conf.paths = [src_dir]
				for s in src_dir.node_path('main').find_iter(prunes = ['todo'], in_pat = '*.cpp'): self.new_obj(s)
				#for h in src_dir.node_path('foo').find_iter(prunes = ['todo'], in_pat = '*.hpp', ex_pat = '*.private.hpp'): print h.path
				return self.in_tasks

	main_prog = MainProg()

	from options import options, known_options, help
	if '--help' in options:
		project.help()
		keys = []
		just = 0
		for k, v in help.iteritems():
			if len(v[0]) > just: just = len(v[0])
			keys.append(k)
		keys.sort()
		just += 1
		for h in keys:
			h = help[h]
			print h[0].ljust(just), h[1]
			if len(h) >= 3: print ''.ljust(just), '(default: ' + h[2] + ')'
		sys.exit(0)
	project.options()
	for o in options:
		if o.startswith('-'):
			e = o.find('=')
			if e >= 0: o = o[:e]
			if o not in known_options:
				print >> sys.stderr, 'unknown option:', o
				sys.exit(1)
	project.conf()
	project.build([main_prog])
	project.dump()

if __name__ == '__main__': main()
