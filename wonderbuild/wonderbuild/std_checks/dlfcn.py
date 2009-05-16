#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import sys

from wonderbuild.cxx_tool_chain import MultiBuildCheckTask, BuildCheckTask
from wonderbuild.signature import Sig
from wonderbuild.logger import silent, is_debug, debug

class DlfcnCheckTask(MultiBuildCheckTask):
	def __init__(self, base_cfg): MultiBuildCheckTask.__init__(self, 'posix-dlfcn', base_cfg)
		
	def do_check_and_set_result(self, sched_ctx):
		t = DlfcnCheckTask.SubCheckTask(self, True)
		sched_ctx.parallel_wait(t)
		if t.result: self.dl, self.result = t.dl, t.result
		else:
			t = DlfcnCheckTask.SubCheckTask(self, False)
			sched_ctx.parallel_wait(t)
			if t.result: self.dl, self.result = t.dl, t.result
			else: self.result = False
	
	@property
	def result_display(self):
		if self.result: return 'yes with' + (not self.dl and 'out' or '') + ' libdl', '32'
		else: return 'no', '31'
		
	def apply_to(self, cfg):
		if self.dl: cfg.libs.append('dl')

	@property
	def source_text(self): return \
		'#include <dlfcn.h>\n' \
		'void dlfcn() {\n' \
		'	void * lib(dlopen("lib", RTLD_LAZY));\n' \
		'	void * sym(dlsym(lib, "sym"));\n' \
		'	char * error(dlerror());\n' \
		'	int result(dlclose(lib));\n' \
		'}'
	
	class SubCheckTask(BuildCheckTask):
		def __init__(self, outer, dl):
			BuildCheckTask.__init__(self, outer.name + '-with' + (not dl and 'out' or '') + '-libdl', outer.base_cfg)
			self.outer = outer
			self.dl = dl

		def apply_to(self, cfg):
			if self.dl: cfg.libs.append('dl')

		@property
		def source_text(self): return self.outer.source_text
