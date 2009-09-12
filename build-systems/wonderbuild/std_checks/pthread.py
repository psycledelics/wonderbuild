#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from wonderbuild.cxx_tool_chain import BuildCheckTask

class PThreadCheckTask(BuildCheckTask):
	def __init__(self, base_cfg): BuildCheckTask.__init__(self, 'posix-thread', base_cfg)

	def apply_to(self, cfg):
		if cfg.kind == 'gcc': # TODO windows/cygwin platforms
			cfg.cxx_flags.append('-pthread')
			cfg.ld_flags.append('-pthread')
		else: cfg.libs.append('pthread')

	@property
	def source_text(self): return '''\
#include <pthread.h>
void pthread() {
	pthread_t self(pthread_self());
}
'''
