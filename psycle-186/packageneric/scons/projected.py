# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

class projected:
	def __init__(self, project):
		from packageneric.scons.project import project as project_
		assert isinstance(project, project_)
		self._project = project
		
	def project(self): return self._project
