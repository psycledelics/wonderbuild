#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2009-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from wonderbuild.cxx_tool_chain import BuildCheckTask

class MultitheadingSupportCheckTask(BuildCheckTask):
	def __init__(self, base_cfg): BuildCheckTask.__init__(self, 'multithreading-support', base_cfg)

	def apply_to(self, cfg):
		# some documentation is available in <boost/config/requires_threads.hpp>
		if cfg.kind == 'gcc':
			if cfg.dest_platform.os in ('win', 'cygwin'):
				cfg.cxx_flags.append('-mthreads')
				cfg.ld_flags.append('-mthreads')
			elif cfg.dest_platform.os == 'sunos':
				cfg.cxx_flags.append('-pthread')
				cfg.ld_flags.append('-pthread')
			else:
				cfg.cxx_flags.append('-pthread')
				cfg.ld_flags.append('-pthread')
		elif cfg.kind == 'msvc':
			cfg.cxx_flags.append('-MD') # TODO -MT, -MTd, -MD, -MDd

	@property
	def source_text(self):
		if cfg.dest_platform.os not in ('win', 'cygwin'):
			return '''\
#if !defined _REENTRANT && !defined _PTHREADS && !defined _MT && !defined __MT__
	#error no multithreading support
#endif

#if defined _REENTRANT
	#include <pthread.h>
	void pthread() {
		pthread_t self(pthread_self());
	}
#endif
'''
