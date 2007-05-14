# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

import os
from dictionary import dictionary

class env(dictionary):
	def add_inherited(self, keys):
		for key in keys:
			try: value = os.environ[key]
			except KeyError: pass
			else: self[key] = value

	def add_paths(self, dictionary_):
		for key, value in dictionary_:
			try: current_value = self[key]
			except KeyError: current_value = ''
			from SCons.Util import AppendPath as append_path_unique
			self[key] = append_path_unique(current_value, value)

_template = {}

def template(base):
	try: return _template[base]
	except KeyError:

		class result(base):
			def __init__(self, project,
				inherited_os_env = None,
				*args, **kw
			):
				base.__init__(*(self, project) + args, **kw)
				if inherited_os_env is not None: self.os_env().add_inherited(inherited_os_env)

			def os_env(self):
				try: return self._os_env
				except AttributeError:
					self._os_env = env()
					return self._os_env
					
			def attach(self, source):
				base.attach(self, source)
				if isinstance(source, result): self.os_env().attach(source.os_env())

			def _scons(self, scons):
				base._scons(self, scons)
				scons_env = scons['ENV']
				env = {}
				for key, value in self.os_env().get().items():
					if scons_env.has_key(key) and 'PATH' in key: # todo kluge
						from SCons.Util import AppendPath as append_path_unique
						env[key] = append_path_unique(scons_env[key], scons.subst(value))
					else:
						env[key] = scons.subst(value)
				scons.Append(ENV = env)
			
		_template[base] = result
		return result
