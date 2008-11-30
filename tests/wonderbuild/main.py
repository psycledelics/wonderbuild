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
			obj = Obj(project)
			obj.source = self.project.src_node.rel_node(os.path.join('src', 'foo', 'foo.cpp'))
			obj.target = self.project.bld_node.rel_node(os.path.join('modules', 'libfoo', 'src', 'foo', 'foo.o'))
			obj.out_tasks = [self]
			self.in_tasks = [obj]
			self.sources = [obj.target]
			return self.in_tasks
				
		def process(self):
			self.target = self.project.bld_node.rel_node(os.path.join('modules', 'libfoo', 'libfoo.so'))
			Lib.process(self)
			
	from project import Project
	project = Project()

	if False:
		n = project.fs.node('src')
		s = n.find_iter(prunes = ['todo'], in_pat = '*.cpp')
		h = n.find_iter(prunes = ['todo'], in_pat = '*.hpp', ex_pat = '*.private.hpp')
		for f in s: print 'sssssssssssss', f.rel_path
		for f in h: print 'hhhhhhhhhhhhh', f.rel_path
		#project.fs.display(False)
		#project.fs.display(True)
		project.dump()
	
	lib_foo = LibFoo(project)
	project.build([lib_foo])
	project.dump()
