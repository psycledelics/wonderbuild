#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

def main():
	import sys, os

	import logger
	from options import options, help
	if '--help' in options:
		for h in help.itervalues(): print h
		sys.exit(0)
	for o in options:
		if o.startswith('-') and not o in help:
			print >> sys.stderr, 'unknown option:', o
			sys.exit(1)

	from cxx_chain import ObjConf, LibConf, Lib

	class LibFoo(Lib):
		def __init__(self, lib_conf): Lib.__init__(self, lib_conf, aliases = ['foo'])
			
		def dyn_in_tasks(self):
			if len(self.in_tasks) != 0: return None
			self.target = self.project.bld_node.rel_node(os.path.join('modules', 'libfoo', 'libfoo.so'))
			self.new_obj(self.project.src_node.rel_node(os.path.join('src', 'foo', 'foo.cpp')))
			self.new_obj(self.project.src_node.rel_node(os.path.join('src', 'main', 'main.cpp')))
			self.obj_conf.paths = [self.project.src_node.rel_node('src')]
			return self.in_tasks
			
	from project import Project
	project = Project()

	if True:
		obj_conf = ObjConf(project)
		lib_conf = LibConf(obj_conf)
		lib_foo = LibFoo(lib_conf)
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
