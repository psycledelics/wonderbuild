#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2010 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from wonderbuild.cxx_tool_chain import BuildCheckTask

class WinMMCheckTask(BuildCheckTask):

	@staticmethod
	def shared_uid(*args, **kw): return 'ms-winmm'

	def __init__(self, persistent, uid, base_cfg): BuildCheckTask.__init__(self, persistent, uid, base_cfg)

	def apply_to(self, cfg): cfg.libs.append('winmm')

	@property
	def source_text(self): return '''\
#include <windows.h>
#include <mmsystem.h>
void microsoft_mm_system() {
	::UINT milliseconds(10);
	::timeBeginPeriod(milliseconds);
	::timeGetTime();
	::timeEndPeriod(milliseconds);
}
'''
