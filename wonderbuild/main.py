#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

def main():
	import sys, os

	from cxx_chain import ObjConf, LibConf, Lib

	class LibFoo(Lib):
		def __init__(self, lib_conf): Lib.__init__(self, lib_conf, 'foo')
			
		def dyn_in_tasks(self):
			if len(self.in_tasks) != 0: return None
			Lib.dyn_in_tasks(self)
			src_dir = self.project.src_node.node_path('src')
			self.obj_conf.paths = [src_dir]
			for s in src_dir.node_path('foo').find_iter(prunes = ['todo'], in_pat = '*.cpp'): self.new_obj(s)
			#for h in src_dir.node_path('foo').find_iter(prunes = ['todo'], in_pat = '*.hpp', ex_pat = '*.private.hpp'): print h.path
			return self.in_tasks
			
	from project import Project
	project = Project()
	obj_conf = ObjConf(project)
	lib_conf = LibConf(obj_conf)
	lib_foo = LibFoo(lib_conf)

	from options import options, help
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
	project.conf()
	for o in options:
		if o.startswith('-'):
			e = o.find('=')
			if e >= 0: o = o[:e]
			if o not in help:
				print >> sys.stderr, 'unknown option:', o
				sys.exit(1)
	project.build([lib_foo])
	project.dump()

if __name__ == '__main__': main()
