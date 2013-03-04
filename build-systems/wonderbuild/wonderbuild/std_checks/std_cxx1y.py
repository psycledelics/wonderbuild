#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2013-2013 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from wonderbuild.cxx_tool_chain import BuildCheckTask

class StdCxx1yCheckTask(BuildCheckTask):

	@staticmethod
	def shared_uid(*args, **kw): return 'std-c++1y'

	def apply_cxx_to(self, cfg):
		if cfg.kind == 'gcc':
			if '-std=c++1y' not in cfg.cxx_flags and '-std=gnu++1y' not in cfg.cxx_flags: cfg.cxx_flags.append('-std=gnu++1y')
		else: pass # TODO other compilers

	@property
	def source_text(self): return '''\
#if !defined __GXX_EXPERIMENTAL_CXX1Y__
	#error c++1y unsupported or not enabled
#endif
'''
