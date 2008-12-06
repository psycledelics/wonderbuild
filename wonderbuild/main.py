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
			src_dir = self.project.src_node.rel_node('src')
			self.obj_conf.paths = [src_dir]
			for s in src_dir.rel_node('foo').find_iter(prunes = ['todo'], in_pat = '*.cpp'): self.new_obj(s)
			return self.in_tasks
			
	from project import Project
	project = Project()
	obj_conf = ObjConf(project)
	lib_conf = LibConf(obj_conf)
	lib_foo = LibFoo(lib_conf)
	project.build([lib_foo])
	project.dump()

if __name__ == '__main__':
	main()
