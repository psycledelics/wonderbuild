#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2011-2011 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from wonderbuild.cxx_tool_chain import BuildCheckTask

class OpenMPCheckTask(BuildCheckTask):

	@staticmethod
	def shared_uid(*args, **kw): return 'openmp'

	def apply_to(self, cfg):
		if cfg.kind == 'gcc':
			cfg.cxx_flags.append('-fopenmp')
			cfg.ld_flags.append('-fopenmp')
		elif cfg.kind == 'msvc':
			cfg.cxx_flags.append('-openmp')
			cfg.ld_flags.append('-openmp')
		else: pass # TODO

	@property
	def source_text(self): return '''\
#if !defined _OPENMP
	#error openmp not enabled or unsupported
#endif
#include <omp.h>
void openmp() {
	// todo do something with it for a complete check
}
'''
