# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

import detail.scons as scons
from packageneric.generic.scons.check import check

base = scons.template(check)

class cxx_build(base):
	def __init__(self, project, name, source_text, **kw):
		base.__init__(self, project = project, name = name, **kw)
		self._source_text = source_text
		
	def source_text(self): return self._source_text
		
	def _scons_sconf_execute(self, scons_sconf_context):
		if not base._scons_sconf_execute(self, scons_sconf_context): return False
		result = scons_sconf_context.TryBuild(builder = scons_sconf_context.env.Program, text = self.source_text() + '\nint main() { return 0; }\n', extension = '.cpp')
		return result, None

	def __str__(self): return self.name() + ': libraries '"'" + ' '.join(self.input_env().linker().libraries().get()) + "'"' and their associated headers'
