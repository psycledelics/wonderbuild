# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006 johan boule <bohan@jabber.org>
# copyright 2006 psycledelics http://psycle.pastnotecut.org

from packageneric.generic.scons.check import check

class external_package(check):
	def __init__(self, project, name, dependencies, distribution_packages, url):
		check.__init__(self, project = project, name = name, dependencies = dependencies)
		self._distribution_packages = distribution_packages
		self._url = url
	
	def distribution_packages(self): return self._distribution_packages
	
	def url(self): return self._url

	def add_dependency(self, check_):
		assert isinstance(check_, check)
		check.add_dependency(self, check_)

	def execute(self):
		if not check.execute(self): return False
		for check_ in filter(lambda x: isinstance(x, check), self.dependencies()): self.input_env().attach(check_.output_env())
		if not self.result():
			dependencies_not_found = []
			for package in self.dependencies():
				if not package.result(): dependencies_not_found.append(str(package))
			if len(dependencies_not_found):
				message = 'the following external packages:'
				for dependency_not_found in dependencies_not_found: message += str(dependency_not_found) + '\n'
				message += 'are needed for the external package:' + str(self)
			else: 
				message = 'the following external package was not found:' + str(self)
			self.project().error(message)
		return True

	def __str__(self):
		line = '____________________'
		bar = '\n|'
		separator = bar + line + bar
		string = bar + ' ' + line + bar + ' '
		from pkg_config import pkg_config
		for pkg_config_ in filter(lambda x: isinstance(x, pkg_config), self.dependencies()): string += bar + ' pkg-config: ' + str(pkg_config_)
		from cxx_build import cxx_build
		for cxx_build_ in filter(lambda x: isinstance(x, cxx_build), self.dependencies()): string += bar + ' ' + str(cxx_build_)
		if self.distribution_packages():
			string += separator
			for (k, v) in self.distribution_packages().items(): string += bar + ' -> on ' + k + ' distributions, the package names are ' + v
		if self.url() is not None:
			if not self.distribution_packages(): string += separator
			string += bar + ' -> '
			if self.distribution_packages(): string += 'otherwize, '
			string += 'the source of this package can be downloaded from ' + self.url()
		string += separator
		return string
