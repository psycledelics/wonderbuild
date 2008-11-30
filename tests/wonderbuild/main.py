#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import sys, os, os.path

from project import Project
from task import Lib

if __name__ == '__main__':
	class LibFoo(Lib):
		def __init__(self, project):
			Lib.__init__(self, project, aliases = ['foo'])
			
		def dyn_in_tasks(self):
			if len(self.in_tasks): return None
			from task import Obj
			
			cxx_paths = [self.project.src_node.rel_node('src')]
			cxx_flags = ['-fPIC']
			out = self.project.bld_node.rel_node(os.path.join('modules', 'libfoo'))

			obj1 = Obj(project)
			obj1.paths = cxx_paths
			obj1.flags = cxx_flags
			obj1.source = self.project.src_node.rel_node(os.path.join('src', 'foo', 'foo.cpp'))
			obj1.target = out.rel_node(os.path.join('src', 'foo', 'foo.o'))
			obj1.out_tasks = [self]

			obj2 = Obj(project)
			obj2.paths = cxx_paths
			obj2.flags = cxx_flags
			obj2.source = self.project.src_node.rel_node(os.path.join('src', 'main', 'main.cpp'))
			obj2.target = out.rel_node(os.path.join('src', 'main', 'main.o'))
			obj2.out_tasks = [self]

			self.in_tasks = [obj1, obj2]
			self.sources = [obj1.target, obj2.target]
			self.target = out.rel_node('libfoo.so')
			self.flags = ['-shared']
			return self.in_tasks
			
	from project import Project
	project = Project()

	lib_foo = LibFoo(project)
	project.build([lib_foo])
		
	if False:
		n = project.fs.node('src')
		s = n.find_iter(prunes = ['todo'], in_pat = '*.cpp')
		h = n.find_iter(prunes = ['todo'], in_pat = '*.hpp', ex_pat = '*.private.hpp')
		for f in s: print 'sssssssssssss', f.path
		for f in h: print 'hhhhhhhhhhhhh', f.path
		x = project.fs.node('../atomic/')
		project.fs.display(False)
		project.fs.display(True)
		print x.path

	project.dump()

