#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

def wonderbuild_script(project):
	tasks = []

	from wonderbuild.cxx_chain import UserCfg, BuildCheckTask, ModTask
	build_cfg = UserCfg(project)

	src_dir = project.src_node.node_path('src')
	build_cfg.include_paths.append(src_dir)

	check_cfg = build_cfg.clone()

	class StdMathCheckTask(BuildCheckTask):
		def __init__(self, base_cfg): BuildCheckTask.__init__(self, 'c++-std-math', base_cfg)

		def apply_to(self, cfg): cfg.libs.append('m')

		@property
		def source_text(self):
			return '''\
				#include <cmath>
				int main() {
					float const f(std::sin(1.f));
					return 0;
				}
				\n'''

	std_math_check = StdMathCheckTask(check_cfg)

	if False and std_math_check.result: std_math_check.apply_to(build_cfg)

	if False:
		pch = CxxPreCompileTask(build_cfg.clone(), src_dir.node_path('pch.hpp'))
		pch.apply_to(build_cfg)
	
		class Pch(ModTask):
			def __init__(self):
				ModTask.__init__(self, 'pch', ModTask.Kinds.PCH, build_cfg)

			@property
			def header(self): src_dir.node_path('pch.hpp')
		pch = Pch()

	class LibFoo(ModTask):
		def __init__(self): ModTask.__init__(self, 'foo', ModTask.Kinds.LIB, build_cfg)

		def __call__(self, sched_ctx):
			yield [std_math_check]
			if std_math_check.result: std_math_check.apply_to(self.cfg)
			for s in src_dir.node_path('foo').find_iter(in_pats = ['*.cpp'], prune_pats = ['todo']): self.sources.append(s)
			for t in ModTask.__call__(self, sched_ctx): yield t
	lib_foo = LibFoo()
	
	class MainProg(ModTask):
		def __init__(self): ModTask.__init__(self, 'main', ModTask.Kinds.PROG, build_cfg)

		def __call__(self, sched_ctx):
			self.dep_lib_tasks.append(lib_foo)
			self.cfg.lib_paths.append(lib_foo.target.parent)
			self.cfg.libs.append(lib_foo.name)
			for s in src_dir.node_path('main').find_iter(in_pats = ['*.cpp'], prune_pats = ['todo']): self.sources.append(s)
			return ModTask.__call__(self, sched_ctx)
	main_prog = MainProg()
	tasks.append(main_prog)

	return tasks
