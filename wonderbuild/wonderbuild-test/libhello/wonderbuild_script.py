#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2009-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from wonderbuild.task import ProjectTask

class Dummy(ProjectTask):
	def __call__(self, sched_ctx):
		print 'libhello dummy task executing'

from wonderbuild.script import ScriptTask

class Wonderbuild(ScriptTask):
	def __call__(self, sched_ctx):
		print 'libhello script task executing'
		self.dummy = Dummy(self.project)
		#self.project.add_task_aliases(self.dummy, 'dummy', 'all')
