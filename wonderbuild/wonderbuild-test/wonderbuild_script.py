#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

def wonderbuild_script(project):

	from wonderbuild.cxx_chain import UserCfg, PkgConfigCheckTask, BuildCheckTask, PreCompileTask, ModTask
	from wonderbuild.std_checks import StdMathCheckTask
	from wonderbuild.install import InstallTask
	
	tasks = []

	glibmm = PkgConfigCheckTask(project, ['glibmm-2.4 >= 2.4'])

	build_cfg = UserCfg(project)

	src_dir = project.src_node / 'src'
	build_cfg.include_paths.append(src_dir)

	check_cfg = build_cfg.clone()
	std_math_check = StdMathCheckTask(check_cfg)

	class Pch(PreCompileTask):
		def __init__(self, pic):
			PreCompileTask.__init__(self, 'pch-' + (not pic and 'non-' or '') + 'pic', build_cfg)
			self.pic = pic

		@property
		def source_text(self):
			try: return self._source_text
			except AttributeError:
				self._source_text = \
					'#include <string>\n' \
					'#include <sstream>\n' \
					'#include <iostream>'
				return self._source_text

		def __call__(self, sched_ctx):
			sched_ctx.parallel_wait((std_math_check, glibmm))
			if std_math_check.result:
				std_math_check.apply_to(self.cfg)
				self.source_text
				self._source_text += '\n#include <cmath>'
			if glibmm.result:
				glibmm.apply_to(self.cfg)
				self.source_text
				self._source_text += '\n#include <glibmm.h>'
			self.cfg.pic = self.pic
			PreCompileTask.__call__(self, sched_ctx)
	pic_pch = non_pic_pch = None
	if build_cfg.shared or build_cfg.pic:
		pic_pch = Pch(pic = True)
		lib_pch = pic_pch
	else:
		non_pic_pch = Pch(pic = False)
		lib_pch = non_pic_pch
	if build_cfg.pic:
		if pic_pch is None: pic_pch = Pch(pic = True)
		prog_pch = pic_pch
	else:
		if non_pic_pch is None: non_pic_pch = Pch(pic = False)
		prog_pch = non_pic_pch

	class LibFooInstallTask(InstallTask):
		def __init__(self): InstallTask.__init__(self, project)

		@property
		def trim_prefix(self): return src_dir

		@property
		def sources(self):
			try: return self._sources
			except AttributeError:
				self._sources = []
				for s in (self.trim_prefix / 'foo').find_iter(in_pats = ['*.hpp'], ex_pats = ['*.private.hpp'], prune_pats = ['todo']): self._sources.append(s)
				return self._sources
		
		@property
		def dest_dir(self): return build_cfg.fhs.include

	class LibFoo(ModTask):
		def __init__(self): ModTask.__init__(self, 'foo', ModTask.Kinds.LIB, build_cfg)

		def __call__(self, sched_ctx):
			sched_ctx.parallel_no_wait((LibFooInstallTask(),))
			sched_ctx.parallel_wait((glibmm, std_math_check, lib_pch))
			lib_pch.apply_to(self.cfg)
			if std_math_check.result: std_math_check.apply_to(self.cfg)
			if glibmm.result: glibmm.apply_to(self.cfg)
			for s in (src_dir / 'foo').find_iter(in_pats = ['*.cpp'], prune_pats = ['todo']): self.sources.append(s)
			ModTask.__call__(self, sched_ctx)
	lib_foo = LibFoo()
	
	class MainProg(ModTask):
		def __init__(self): ModTask.__init__(self, 'main', ModTask.Kinds.PROG, build_cfg)

		def __call__(self, sched_ctx):
			sched_ctx.parallel_no_wait((lib_foo,))
			sched_ctx.parallel_wait((prog_pch, glibmm))
			prog_pch.apply_to(self.cfg)
			if glibmm.result: glibmm.apply_to(self.cfg)
			self.dep_lib_tasks.append(lib_foo)
			for s in (src_dir / 'main').find_iter(in_pats = ['*.cpp'], prune_pats = ['todo']): self.sources.append(s)
			ModTask.__call__(self, sched_ctx)
	main_prog = MainProg()
	tasks.append(main_prog)

	return tasks
