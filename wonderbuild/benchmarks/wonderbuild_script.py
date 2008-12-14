#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

def main():
	import sys, os
	sys.path.append(os.path.split(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))[0])

	from wonderbuild.project import Project
	project = Project()

	from wonderbuild.cxx_chain import BaseObjConf, BaseModConf
	base_obj_conf = BaseObjConf(project)
	base_mod_conf = BaseModConf(base_obj_conf)

	from wonderbuild.cxx_chain import PkgConf, ObjConf, ModConf, Mod

	top_src_dir = project.src_node.node_path('bench')

	class BenchLib(Mod):
		def __init__(self, name): Mod.__init__(self, ModConf(base_mod_conf, BenchLib.BenchObjConf(base_obj_conf), 'lib'), name)
		
		def dyn_in_tasks(self):
			if len(self.in_tasks) != 0: return None
			Mod.dyn_in_tasks(self)
			src_dir = top_src_dir.node_path(self.name)
			self.obj_conf.paths.append(src_dir)
			for s in src_dir.find_iter(in_pat = '*.cpp'): self.new_obj(s)
			return self.in_tasks

		class BenchObjConf(ObjConf):
			def conf(self):
				ObjConf.conf(self)
				self.paths.append(top_src_dir)

	bench_libs = []
	for s in top_src_dir.actual_children:
		if s.startswith('lib_'): bench_libs.append(BenchLib(s))
	
	project.conf()
	project.build(bench_libs)
	project.dump()

	'''
		import cProfile, pstats
		cProfile.run("import Build\nBuild.bld.flush()", 'profi.txt')
		p = pstats.Stats('profi.txt')
		p.sort_stats('cumulative').print_stats(80)
	'''

if __name__ == '__main__':
	main()
