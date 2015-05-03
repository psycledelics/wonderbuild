#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2013 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from wonderbuild.cxx_tool_chain import BuildCheckTask

# gcc -E -dM -std=c++11 -x c++-header /dev/null | sort

class AutoLinkSupportCheckTask(BuildCheckTask):

	@staticmethod
	def shared_uid(*args, **kw): return 'auto-link-support'

	def __init__(self, persistent, uid, base_cfg): BuildCheckTask.__init__(self, persistent, uid, base_cfg, compile=False)

	@property
	def source_text(self):
		return '''\
// check below is the same as in <boost/config/auto_link.hpp>
#if !( \\
		defined __BORLANDC__ || \\
		__MWERKS__ >= 0x3000 && _WIN32 || \\
		defined __ICL && defined _MSC_EXTENSIONS && _MSC_VER >= 1200 || \\
		!defined __ICL && defined _MSC_VER \\
)
	#error no auto link support
#endif
'''
