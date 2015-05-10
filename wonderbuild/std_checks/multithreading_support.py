#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2009-2011 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from wonderbuild.cxx_tool_chain import BuildCheckTask

class MultithreadingSupportCheckTask(BuildCheckTask):

	@staticmethod
	def shared_uid(*args, **kw): return 'multithreading-support'

	def apply_cxx_to(self, cfg):
		# some documentation is available in <boost/config/requires_threads.hpp>
		if cfg.kind == 'gcc':
			if cfg.dest_platform.os in ('win', 'cygwin'):
				cfg.cxx_flags.append('-mthreads')
			elif cfg.dest_platform.os == 'solaris':
				cfg.cxx_flags.append('-pthread')
			else:
				cfg.cxx_flags.append('-pthread')
		elif cfg.kind == 'msvc':
			cfg.cxx_flags.append('-MD') # choice between -MT, -MTd, -MD, -MDd

	def apply_mod_to(self, cfg):
		# some documentation is available in <boost/config/requires_threads.hpp>
		if cfg.kind == 'gcc':
			if cfg.dest_platform.os in ('win', 'cygwin'):
				cfg.ld_flags.append('-mthreads')
			elif cfg.dest_platform.os == 'solaris':
				cfg.ld_flags.append('-pthread')
			else:
				cfg.ld_flags.append('-pthread')

	@property
	def source_text(self):
		if self.base_cfg.dest_platform.os in ('win', 'cygwin'):
			return '/* no way to detect multithreading support in this os */'
		else:
			return '''\
#if !defined _REENTRANT && !defined _PTHREADS && !defined _MT && !defined __MT__
	#error no multithreading support
#endif

#if 0 // better check
	#include <unistd.h>
	#if !defined _POSIX_THREADS
		#error no posix threads support
	#endif
#endif

#if defined _REENTRANT
	#include <pthread.h>
	void pthread() {
		pthread_t self(pthread_self());
	}
#endif
'''

class PThreadCheckTask(BuildCheckTask):

	@staticmethod
	def shared_uid(*args, **kw): return 'posix-thread'

	def apply_cxx_to(self, cfg):
		if cfg.kind == 'gcc': cfg.cxx_flags.append('-pthread')
		else: cfg.defines['_REENTRANT'] = '1'

	def apply_mod_to(self, cfg):
		if cfg.kind == 'gcc': cfg.ld_flags.append('-pthread')
		else: cfg.libs.append('pthread')

	@property
	def source_text(self): return '''\
#if 0 // better check
	#include <unistd.h>
	#if !defined _POSIX_THREADS
		#error no posix threads support
	#endif
#endif

#include <pthread.h>
void pthread() {
	pthread_t self(pthread_self());
}
'''

