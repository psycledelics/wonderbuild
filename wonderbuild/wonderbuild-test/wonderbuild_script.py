#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

def wonderbuild_script(project):
	tasks = []

	from wonderbuild.cxx_chain import UserCfg, BuildCheckTask, PreCompileTask, ModTask
	build_cfg = UserCfg(project)

	src_dir = project.src_node.node_path('src')
	build_cfg.include_paths.append(src_dir)

	check_cfg = build_cfg.clone()

	from wonderbuild.logger import silent
	class StdMathCheckTask(BuildCheckTask):
		def __init__(self, base_cfg): BuildCheckTask.__init__(self, 'c++-std-math', base_cfg)

		def apply_to(self, cfg):
			self.result
			if self.m: cfg.libs.append('m')

		class SubCheckTask(BuildCheckTask):
			def __init__(self, m, name, base_cfg, silent):
				BuildCheckTask.__init__(self, name, base_cfg, silent)
				self.m = m

			def apply_to(self, cfg):
				if self.m: cfg.libs.append('m')

			@property
			def source_text(self):
				return '''\
					#include <cmath>
					int main() {
						float const f(std::sin(1.f));
						return 0;
					}
					\n'''
			
		def __call__(self, sched_ctx):
			self.t0 = StdMathCheckTask.SubCheckTask(False, self.name + '-without-libm', self.base_cfg, silent = True)
			self.t1 = StdMathCheckTask.SubCheckTask(True, self.name + '-with-libm', self.base_cfg, silent = True)
			yield [self.t0, self.t1]
			if not silent:
				self.cfg.print_desc('checking for ' + self.name)
				if self.result: self.cfg.print_result_desc('yes with' + (self.m and '' or 'out') + ' libm\n', '32')
				else: self.cfg.print_result_desc('no\n', '31')
			raise StopIteration

		@property
		def result(self):
			try: return self._result
			except AttributeError:
				self._result = self.t0.result or self.t1.result
				if self.t0.result: self.m = False
				elif self.t1.result: self.m = True
				else: self.m = None

	std_math_check = StdMathCheckTask(check_cfg)

	if False and std_math_check.result: std_math_check.apply_to(build_cfg)

	class Pch(PreCompileTask):
		def __init__(self): PreCompileTask.__init__(self, src_dir.node_path('pch.hpp'), build_cfg.clone())

		def apply_to(self, cfg):
			if std_math_check.result:
				std_math_check.apply_to(cfg)
				PreCompileTask.apply_to(self, cfg)

		def __call__(self, sched_ctx):
			yield [std_math_check]
			if not std_math_check.result: raise StopIteration
			for t in PreCompileTask.__call__(self, sched_ctx): yield t
			#raise StopIteration
	pch = Pch()
	#pch.apply_to(build_cfg)

	class LibFoo(ModTask):
		def __init__(self): ModTask.__init__(self, 'foo', ModTask.Kinds.LIB, build_cfg)

		def __call__(self, sched_ctx):
			yield [std_math_check, pch]
			pch.apply_to(self.cfg)
			if std_math_check.result: std_math_check.apply_to(self.cfg)
			for s in src_dir.node_path('foo').find_iter(in_pats = ['*.cpp'], prune_pats = ['todo']): self.sources.append(s)
			for t in ModTask.__call__(self, sched_ctx): yield t
			#raise StopIteration
	lib_foo = LibFoo()
	
	class MainProg(ModTask):
		def __init__(self): ModTask.__init__(self, 'main', ModTask.Kinds.PROG, build_cfg)

		def __call__(self, sched_ctx):
			yield [pch]
			pch.apply_to(self.cfg)
			self.dep_lib_tasks.append(lib_foo)
			self.cfg.lib_paths.append(lib_foo.target.parent)
			self.cfg.libs.append(lib_foo.name)
			for s in src_dir.node_path('main').find_iter(in_pats = ['*.cpp'], prune_pats = ['todo']): self.sources.append(s)
			for t in ModTask.__call__(self, sched_ctx): yield t
			#raise StopIteration
	main_prog = MainProg()
	tasks.append(main_prog)

	return tasks
