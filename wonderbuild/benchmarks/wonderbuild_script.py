#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

def wonderbuild_script(project):
	from cxx_chain import BaseCxxCfg, BaseModCfg, PkgCfg, CxxCfg, ModCfg, ModTask

	base_cxx_cfg = BaseCxxCfg(project)
	base_mod_cfg = BaseModCfg(base_cxx_cfg)

	top_src_dir = project.src_node.node_path('bench-wonderbuild')

	class BenchLib(ModTask):
		def __init__(self, name): ModTask.__init__(self, ModCfg(base_mod_cfg, BenchLib.BenchCxxCfg(base_cxx_cfg), 'lib'), name)
		
		def dyn_in_tasks(self):
			src_dir = top_src_dir.node_path(self.name)
			for s in src_dir.find_iter(in_pat = '*.cpp'): self.add_new_cxx_task(s)
			return self.in_tasks

		class BenchCxxCfg(CxxCfg):
			def configure(self):
				CxxCfg.configure(self)
				self.paths.append(top_src_dir)

	bench_libs = []
	for s in top_src_dir.actual_children:
		if s.startswith('lib_'): bench_libs.append(BenchLib(s))
	
	return bench_libs
