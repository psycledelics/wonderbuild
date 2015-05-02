#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2013 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from wonderbuild.cxx_tool_chain import MultiBuildCheckTask, BuildCheckTask, ok_color, failed_color

class DynamicLoadingSupportCheckTask(MultiBuildCheckTask):

	@staticmethod
	def shared_uid(*args, **kw): return 'dynamic-loading-support'

	def do_set_deps(self, sched_ctx):
		if self.base_cfg.dest_platform.os != 'win':
			dlfcn = DlfcnCheckTask.shared(self.base_cfg)
			for x in sched_ctx.parallel_wait(dlfcn): yield x
			self.private_deps = [dlfcn]
		self._dlfcn = dlfcn

	@property
	def dl(self):
		if self._dlfcn is None: return None
		else: return self._dlfcn.dl

	def apply_mod_to(self, cfg):
		if self._dlfcn is not None: self._dlfcn.apply_mod_to(cfg)

class DlfcnCheckTask(MultiBuildCheckTask):

	@staticmethod
	def shared_uid(*args, **kw): return 'posix-dlfcn'

	def do_set_deps(self, sched_ctx):
		t = DlfcnCheckTask.SubCheckTask.shared(self, True)
		for x in sched_ctx.parallel_wait(t): yield x
		if not t:
			t = DlfcnCheckTask.SubCheckTask.shared(self, False)
		self.private_deps = [t]
		self._t = t

	def do_check_and_set_result(self, sched_ctx):
		if False: yield x

	@property
	def dl(self): return self._t.dl

	@property
	def result_display(self):
		if self: return 'yes with' + (not self.dl and 'out' or '') + ' ldl', ok_color
		else: return 'no', failed_color
		
	def apply_mod_to(self, cfg): self._t.apply_mod_to(cfg)

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
