# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006 johan boule <bohan@jabber.org>
# copyright 2006 psycledelics http://psycle.pastnotecut.org

from check.external_package import external_package as external_package_check

class local_package(external_package_check):
	def __init__(self, pkg_config_package):
		import check.pkg_config
		pkg_config = filter(lambda x: isinstance(x, check.pkg_config.pkg_config), pkg_config_package.dependencies())
		if not len(pkg_config): dependencies = None
		else: dependencies = [check.pkg_config.pkg_config(pkg_config_package.project(), name = ' '.join([pkg_config.name() for pkg_config in pkg_config]))]
		external_package_check.__init__(self, pkg_config_package.project(),
			name = pkg_config_package.name(),
			dependencies = dependencies,
			distribution_packages = {},
			url = None
		)
		self.output_env().attach(pkg_config_package.uninstalled_env())
		self.targets().extend(pkg_config_package.targets())
