#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

def wonderbuild_script(project):
	src_dir = project.src_node.node_path('src')
	tasks = []

	from wonderbuild.cxx_chain import UserCfg, ModTask
	build_cfg = UserCfg(project)

	if False:
		check_cfg = build_cfg.clone()

		class StdMathCheck(BuildCheck):
			def __init__(self, base_build_cfg): BuildCheck.__init__(self, 'c++-std-math', base_build_cfg)

			def apply_to(self, build_cfg): build_cfg.link.libs.append('m')

			@property
			def source(self):
				return '''\
					#include <cmath>
					int main() {
						float const f(std::sin(1f));
						return 0;
					}
					\n'''

		std_math_check = StdMathCheck(check_cfg)
		if std_math_check.result: std_math_check.apply_to(build_cfg)
		build_cfg.add_in_task(std_math_check)

		build_cfg.cxx.include_paths.append(src_dir)

		pch = CxxPreCompileTask(build_cfg.clone(), src_dir.node_path('pch.hpp'))
		pch.apply_to(build_cfg)
	
		class Pch(ModTask):
			def __init__(self):
				ModTask.__init__(self, 'pch', ModTask.Kinds.PCH, build_cfg)

			@property
			def header(self): src_dir.node_path('pch.hpp')
		pch = Pch()

	build_cfg.impl.build_check(build_cfg,
		'''\
			int main() {
				#warning test
				return 0;
			}
		\n''')

	class LibFoo(ModTask):
		def __init__(self):
			ModTask.__init__(self, 'foo', ModTask.Kinds.LIB, build_cfg)
			#self.client_of(pch)

		def dyn_in_tasks(self, sched_ctx):
			for s in src_dir.node_path('foo').find_iter(in_pats = ['*.cpp'], prune_pats = ['todo']): self.sources.append(s)
			return ModTask.dyn_in_tasks(self, sched_ctx)
	lib_foo = LibFoo()
	
	class MainProg(ModTask):
		def __init__(self):
			ModTask.__init__(self, 'main', ModTask.Kinds.PROG, build_cfg)
			#self.client_of(pch)

		def dyn_in_tasks(self, sched_ctx):
			#self.client_of(lib_foo)
			self.add_in_task(lib_foo)
			self.cfg.include_paths = [src_dir]
			self.cfg.lib_paths.append(lib_foo.target.parent)
			self.cfg.libs.append(lib_foo.name)
			for s in src_dir.node_path('main').find_iter(in_pats = ['*.cpp'], prune_pats = ['todo']): self.sources.append(s)
			return ModTask.dyn_in_tasks(self, sched_ctx)
	main_prog = MainProg()
	tasks.append(main_prog)

	return tasks
