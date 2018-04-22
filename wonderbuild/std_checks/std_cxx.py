#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2013-2015 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from wonderbuild.cxx_tool_chain import BuildCheckTask

class StdCxxCheckTask(BuildCheckTask):

	default_min_version = 14

	@staticmethod
	def shared_uid(base_cfg, min_version=default_min_version): return 'std-c++' + str(min_version)

	def __init__(self, persistent, uid, base_cfg, min_version=default_min_version):
		BuildCheckTask.__init__(self, persistent, uid, base_cfg)
		self.min_version = min_version

	def apply_cxx_to(self, cfg):
		if cfg.kind == 'gcc':
			if (
				'-std=c++' + str(self.min_version) not in cfg.cxx_flags and
				'-std=gnu++' + str(self.min_version) not in cfg.cxx_flags
			): cfg.cxx_flags.append('-std=gnu++' + str(self.min_version))
		else: pass # TODO other compilers

	@property
	def help(self): return 'C++' + str(self.min_version) + ' support'

	@property
	def source_text(self):
		if self.min_version == 14: precise_version = '201402L'
		elif self.min_version == 11: precise_version = '201103L'
		else: precise_version = str(self.min_version)
		
		return '''\
#if __cplusplus < %s
	#error c++%s unsupported or not enabled
#endif
''' % precise_version, str(self.min_version)
