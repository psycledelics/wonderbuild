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
			src = self.project.fs.src_node('unit_tests')
			foo = src.built_node('foo/foo.o')
			self.sources = [foo]
			obj = Obj(project)
			obj.target = foo
			self.in_tasks = [obj]
			for t in self.in_tasks:
				t.source = t.target.src_node_ext('.cpp')
				t.out_tasks = [self]
				
		def process(self):
			self.target = self.project.fs.built_node('libfoo.so')
			Lib.process(self)
			
	from project import Project
	project = Project()
	lib_foo = LibFoo(project)
	project.build(project.tasks)
	project.dump()
