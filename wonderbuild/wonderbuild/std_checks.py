#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2007-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from cxx_chain import BuildCheckTask
from signature import Sig
from logger import silent, is_debug, debug

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
		changed = False
		try: old_sig, self._result, self.m = self.project.state_and_cache[self.uid]
		except KeyError: changed = True
		else:
			if old_sig != self.sig: changed = True
		if not changed:
			if __debug__ and is_debug: debug('task: skip: no change: ' + self.name)
		else:
			self.t0 = StdMathCheckTask.SubCheckTask(False, self.name + '-without-libm', self.base_cfg, silent = True)
			self.t1 = StdMathCheckTask.SubCheckTask(True, self.name + '-with-libm', self.base_cfg, silent = True)
			yield (self.t0, self.t1)
			if not silent:
				self.cfg.print_desc('checking for ' + self.name)
				if self.result: self.cfg.print_result_desc('yes with' + (self.m and '' or 'out') + ' libm\n', '32')
				else: self.cfg.print_result_desc('no\n', '31')
			self.project.state_and_cache[self.uid] = self.sig, self.result, self.m
		raise StopIteration

	@property
	def result(self):
		try: return self._result
		except AttributeError:
			self._result = self.t0.result or self.t1.result
			if self.t0.result: self.m = False
			elif self.t1.result: self.m = True
			else: self.m = None

	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			sig = Sig()
			sig.update(self.base_cfg.cxx_sig)
			sig.update(self.base_cfg.ld_sig)
			sig = self._sig = sig.digest()
			return sig
