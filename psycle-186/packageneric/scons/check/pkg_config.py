# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

import detail.scons as scons
from packageneric.scons.check import check

base = scons.template(check)

class pkg_config(base):
	def __init__(self, project, name, **kw):
		try: inherited_os_env_paths = kw['inherited_os_env_paths']
		except KeyError: kw['inherited_os_env_paths'] = ['PKG_CONFIG_PATH', 'PATH']
		else:
			if 'PKG_CONFIG_PATH' not in inherited_os_env_paths: inherited_os_env_paths.append('PKG_CONFIG_PATH')
			if 'PATH' not in inherited_os_env_paths: inherited_os_env_paths.append('PATH')
		#base.__init__(self, project = project, name = name, pkg_config = [name], **kw)
		base.__init__(self, project = project, name = name, **kw)
				
	def _scons_sconf_execute(self, scons_sconf_context):
		if not base._scons_sconf_execute(self, scons_sconf_context): return False
		result, output = scons_sconf_context.TryAction(self.execute_env().pkg_config_program() + ' --exists "' + self.name() + '"') # or ' '.join(self.execute_env().pkg_config().get())
		return result, output

	def output_env(self):
		try: return self._output_env
		except AttributeError:
			self._output_env = base.output_env(self)
			self._output_env.pkg_config().add([self.name()])
			return self._output_env

	def __str__(self): return 'pkg-config: ' + self.name()
