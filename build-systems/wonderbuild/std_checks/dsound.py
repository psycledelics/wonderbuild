#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from wonderbuild.cxx_tool_chain import BuildCheckTask

class DSoundCheckTask(BuildCheckTask):

	@staticmethod
	def shared_uid(base_cfg, min_version='Ox900', *args, **kw): return 'ms-dsound-' + str(min_version)

	def __init__(self, base_cfg, min_version='Ox900'):
		BuildCheckTask.__init__(self, base_cfg, self.shared_uid(base_cfg, min_version))
		self.min_version = min_version

	def apply_to(self, cfg): cfg.libs.append('dsound')

	@property
	def source_text(self): return '''\
#include <dsound.h>
#if DIRECTSOUND_VERSION < %s
	#error microsoft direct sound version too old
#endif
void microsoft_direct_sound() {
	// todo do something with it for a complete check
}
''' % str(self.min_version)
