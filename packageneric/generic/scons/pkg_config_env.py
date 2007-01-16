# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

_template = {}

def template(base): # chain, os_env
	try: return _template[base]
	except KeyError:
		
		class result(base):
			def __init__(self, project,
				pkg_config = None,
				*args, **kw
			):
				base.__init__(*(self, project) + args, **kw)
				if pkg_config is not None: self.pkg_config().add(pkg_config)
				try: self.__class__._pkg_config_program
				except AttributeError:
					if True or project.platform() != 'cygwin': self.__class__._pkg_config_program = 'pkg_config'
					else:
						import os
						self.__class__._pkg_config_program = project._scons().WhereIs('pkg-config', os.environ['PATH'], reject = ['/bin/pkg-config', '/usr/bin/pkg-config'])
						project.trace('selecting pkg-config: ' + self.__class__._pkg_config_program)

			def pkg_config_program(self):
				return self.__class__._pkg_config_program
				
			def pkg_config(self):
				try: return self._pkg_config
				except AttributeError:
					from set import set
					self._pkg_config = set()
					for attached in self._attached:
						if isinstance(attached, result): self._pkg_config.attach(attached.pkg_config())
					return self._pkg_config
			
			def attach(self, source):
				base.attach(self, source)
				if isinstance(source, result):
					try: pkg_config = self._pkg_config
					except AttributeError: pass
					else: pkg_config.attach(source.pkg_config())
					
			def _scons(self, scons):
				base._scons(self, scons)

				if len(self.pkg_config().get()):
					if self.link_with_static_libraries().get(): static = '--static '
					else: static = ''

					# unlike builders, scons.ParseConfig inherits os.environ and not the ENV var, so we set os.environ temporarily

					import os
					save_path = os.environ.get('PATH', '')
					save_pkg_config_path = os.environ.get('PKG_CONFIG_PATH', '')

					from SCons.Util import AppendPath as append_path_unique

					try: os.environ['PATH'] = append_path_unique(save_path, self.os_env()['PATH'])
					except KeyError: pass

					try: os.environ['PKG_CONFIG_PATH'] = append_path_unique(save_pkg_config_path, self.os_env()['PKG_CONFIG_PATH'])
					except KeyError: pass

					try: scons.ParseConfig(self.pkg_config_program() + ' --cflags --libs ' + static + '"' + ' '.join(self.pkg_config().get()) + '"')
					finally:
						os.environ['PATH'] = save_path
						os.environ['PKG_CONFIG_PATH'] = save_pkg_config_path
				
		_template[base] = result
		return result
