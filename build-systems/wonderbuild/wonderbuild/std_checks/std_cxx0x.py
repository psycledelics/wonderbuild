#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2011-2011 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from wonderbuild.cxx_tool_chain import BuildCheckTask

class StdCxx0xCheckTask(BuildCheckTask):

	@staticmethod
	def shared_uid(*args, **kw): return 'std-c++0x'

	def apply_cxx_to(self, cfg):
		if cfg.kind == 'gcc':
			if '-std=c++0x' not in cfg.cxx_flags and '-std=gnu++0x' not in cfg.cxx_flags: cfg.cxx_flags.append('-std=gnu++0x')
		else: pass # TODO

	@property
	def source_text(self): return '''\
#if __cplusplus <= 199711 && !defined __GXX_EXPERIMENTAL_CXX0X__
	#error c++Ox not enabled or unsupported
#endif
'''
