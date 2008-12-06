#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

def main():
	import sys

	import logger
	from options import options, help
	if '--help' in options:
		for h in help.itervalues():
			print h
		sys.exit(0)
	for o in options:
		if o.startswith('-') and not o in help:
			print >> sys.stderr, 'unknown option:', o
			sys.exit(1)

	from task import Lib, CxxObj
	class LibFoo(Lib):
		def __init__(self, project):
			Lib.__init__(self, project, aliases = ['foo'])
			
		def dyn_in_tasks(self):
			if len(self.in_tasks): return None
			
			import os

			self.shared = True

			cxx_paths = [self.project.src_node.rel_node('src')]
			cxx_flags = ['-fPIC']
			out = self.project.bld_node.rel_node(os.path.join('modules', 'libfoo'))

			obj1 = CxxObj(project)
			obj1.paths = cxx_paths
			obj1.pic = self.shared
			obj1.source = self.project.src_node.rel_node(os.path.join('src', 'foo', 'foo.cpp'))
			obj1.target = out.rel_node(os.path.join('src', 'foo', 'foo.o'))

			obj2 = CxxObj(project)
			obj2.paths = cxx_paths
			obj2.pic = self.shared
			obj2.source = self.project.src_node.rel_node(os.path.join('src', 'main', 'main.cpp'))
			obj2.target = out.rel_node(os.path.join('src', 'main', 'main.o'))

			self.add_in_task(obj1)
			self.add_in_task(obj2)
			self.sources = [obj1.target, obj2.target]
			self.target = out.rel_node('libfoo.so')
			return self.in_tasks
			
	from project import Project
	project = Project()

	if True:
		lib_foo = LibFoo(project)
		project.build([lib_foo])
	else:
		n = project.src_node.rel_node('src')
		s = n.find_iter(prunes = ['todo'], in_pat = '*.cpp')
		h = n.find_iter(prunes = ['todo'], in_pat = '*.hpp', ex_pat = '*.private.hpp')
		for f in s: print 'sssssssssssss', f.path
		for f in h: print 'hhhhhhhhhhhhh', f.path
		x = project.src_node.rel_node('../tests')
		y = project.src_node.rel_node('../wonderbuild')
		project.fs.display(False)
		project.fs.display(True)
		print x.path
		print y.path

	project.dump()

if __name__ == '__main__':
	main()
