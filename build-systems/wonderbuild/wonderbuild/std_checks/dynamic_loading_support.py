#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2011 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from wonderbuild.cxx_tool_chain import MultiBuildCheckTask, BuildCheckTask, ok_color, failed_color

class DynamicLoadingSupportCheckTask(MultiBuildCheckTask):

	@staticmethod
	def shared_uid(*args, **kw): return 'dynamic-loading-support'

	def do_check_and_set_result(self, sched_ctx):
		if self.base_cfg.dest_platform.os == 'win':
			self.results = True, None
		else:
			dlfcn = DlfcnCheckTask.shared(self.base_cfg)
			for x in sched_ctx.parallel_wait(dlfcn): yield x
			self.results = dlfcn.results
			
	@property
	def result(self): return self.results[0]
	
	@property
	def dl(self): return self.results[1]

	def apply_mod_to(self, cfg):
		if self.dl: cfg.libs.append('dl')

class DlfcnCheckTask(MultiBuildCheckTask):

	@staticmethod
	def shared_uid(*args, **kw): return 'posix-dlfcn'

	def do_check_and_set_result(self, sched_ctx):
		t = DlfcnCheckTask.SubCheckTask.shared(self, True)
		for x in sched_ctx.parallel_wait(t): yield x
		if t.result: self.results = t.result, t.dl
		else:
			t = DlfcnCheckTask.SubCheckTask.shared(self, False)
			for x in sched_ctx.parallel_wait(t): yield x
			if t.result: self.results = t.result, t.dl
			else: self.results = False, None
	
	@property
	def result(self): return self.results[0]
	
	@property
	def dl(self): return self.results[1]

	@property
	def result_display(self):
		if self.result: return 'yes with' + (not self.dl and 'out' or '') + ' ldl', ok_color
		else: return 'no', failed_color
		
	def apply_mod_to(self, cfg):
		if self.dl: cfg.libs.append('dl')

	@property
	def source_text(self): return '''\
#include <dlfcn.h>
void dlfcn() {
	void * lib(dlopen("lib", RTLD_LAZY));
	void * sym(dlsym(lib, "sym"));
	char * error(dlerror());
	int result(dlclose(lib));
	int const modes(
		RTLD_LAZY || RTLD_NOW || RTLD_GLOBAL || RTLD_LOCAL
		#if defined RTLD_DEFAULT && defined RTLD_NEXT
			|| RTLD_DEFAULT || RTLD_NEXT
		#endif
	);
}
'''
	
	class SubCheckTask(BuildCheckTask):
		@staticmethod
		def shared_uid(outer, dl): return outer.uid + '-with' + (not dl and 'out' or '') + '-ldl'
		
		@classmethod
		def shared(class_, outer, dl): return BuildCheckTask._shared(class_, outer.base_cfg, outer, dl)

		def __init__(self, persistent, uid, outer, dl):
			BuildCheckTask.__init__(self, persistent, uid, outer.base_cfg)
			self.outer = outer
			self.dl = dl

		def apply_mod_to(self, cfg):
			if self.dl: cfg.libs.append('dl')

		@property
		def source_text(self): return self.outer.source_text
