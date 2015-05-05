#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2013 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from wonderbuild.cxx_tool_chain import MultiBuildCheckTask, BuildCheckTask, ok_color, failed_color

class StdMathCheckTask(MultiBuildCheckTask):

	@staticmethod
	def shared_uid(*args, **kw): return 'std-math'

	def do_set_deps(self, sched_ctx):
		t = StdMathCheckTask.SubCheckTask.shared(self, True)
		for x in sched_ctx.parallel_wait(t): yield x
		if not t:
			t = StdMathCheckTask.SubCheckTask.shared(self, False)
		self.private_deps = [t]
		self._t = t

	@property
	def m(self): return self._t.m

	@property
	def result_display(self):
		if self: return 'yes with' + (not self.m and 'out' or '') + ' lm', ok_color
		else: return 'no', failed_color
		
	def apply_mod_to(self, cfg): self._t.apply_mod_to(cfg)

	@property
	def source_text(self):
		if self.base_cfg.lang in ('c++', 'objective-c++'):
			return '''\
#include <cmath>
double math() {
	float  const f(std::sin(1.f));
	double const d(std::sin(1. ));
	return d + f;
}
'''
		else: return '''\
#include <math.h>
double math() {
	float  const f = sinf(1.f);
	double const d = sin (1. );
	return d + f;
}
'''

	class SubCheckTask(BuildCheckTask):
		@staticmethod
		def shared_uid(outer, m): return outer.uid + '-with' + (not m and 'out' or '') + '-lm'
		
		@classmethod
		def shared(class_, outer, m): return BuildCheckTask._shared(class_, outer.base_cfg, outer, m)

		def __init__(self, persistent, uid, outer, m):
			BuildCheckTask.__init__(self, persistent, uid, outer.base_cfg)
			self.outer = outer
			self.m = m

		def apply_mod_to(self, cfg):
			if self.m: cfg.libs.append('m')

		@property
		def source_text(self): return self.outer.source_text
