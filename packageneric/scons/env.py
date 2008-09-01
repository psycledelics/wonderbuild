# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

from projected import projected
from attachable import attachable

class env(projected, attachable):
	def __init__(self, project, *args, **kw):
		projected.__init__(self, project)
		attachable.__init__(self)
		if len(args): project.warning('unexpected arguments: ' + str(args))
		if len(kw): project.warning('unrecognised keywords: ' + str(kw))
		# todo print a stack trace after the warnings

	def attach(self, source):
		assert isinstance(source, env)
		attachable.attach(self, source)

	def attached(self, *args, **kw): return attachable.attached(self, self.project(), *args, **kw)

	def _scons(self, scons): pass

	def env_class(): return env
	env_class = staticmethod(env_class)
