# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

from check.external_package import external_package as external_package_check

class local_package(external_package_check):
	def __init__(self, pkg_config_package):
		external_package_check.__init__(self, pkg_config_package.project(),
			name = pkg_config_package.name(),
			dependencies = [],
			distribution_packages = {},
			url = None
		)
		self._pkg_config_package = pkg_config_package
		
	def output_env(self):
		try: return self._local_package_output_env
		except AttributeError:
			self._local_package_output_env = external_package_check.output_env(self)
			self._pkg_config_package.targets() # todo klugde. it is probably best to be triggered from the result() method.
			# The underlying pkg_config_package contains modules that:
			# - define some env settings
			# - have dependencies of type check that define an output_env to attach
			self._local_package_output_env.attach(self._pkg_config_package.uninstalled_env())
			#self._output_env.attach(self._pkg_config_package.installed_env())
			if False:
				print 'xxxxxxxxxxxx -I', self._local_package_output_env.compilers().cxx().paths()
				print 'xxxxxxxxxxxx -L', self._local_package_output_env.linker().paths()
			return self._local_package_output_env
		
	def installed_env(self):
		try: return self._installed_env
		except AttributeError:
			self._installed_env = external_package_check.output_env(self)
			self._installed_env.attach(self._pkg_config_package.installed_env())
			return self._installed_env
		
	def targets(self): return self._pkg_config_package.targets()
