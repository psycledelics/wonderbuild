# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006 johan boule <bohan@jabber.org>
# copyright 2006 psycledelics http://psycle.pastnotecut.org

from attachable import attachable

class env(attachable):
	def __init__(self, project, *args, **kw):
		from packageneric.generic.scons.project import project as project_
		assert isinstance(project, project_)
		self._project = project
		if len(args): project.warning('*args: ' + str(args))
		if len(kw): project.warning('**kw: ' + str(kw))
		
	def project(self): return self._project

	def attach(self, source): assert isinstance(source, env)

	def attached(self, *args, **kw): return attachable.attached(self, self.project(), *args, **kw)

	def _scons(self, scons): pass
