# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

from packageneric.generic.scons.check import check

class external_package(check):
	def __init__(self, project, name, dependencies, distribution_packages, url):
		check.__init__(self, project = project, name = name, dependencies = dependencies)
		self._distribution_packages = distribution_packages
		self._url = url
	
	def distribution_packages(self): return self._distribution_packages
	
	def url(self): return self._url

	def execute(self):
		if not check.execute(self): return False
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
		string = ' ' + line + bar + ' '
		for check_ in filter(lambda x: not isinstance(x, external_package), self.dependencies()): string += bar + ' ' + str(check_)
		separator = bar + line + bar
		provided = separator + bar + ' provided by external package: ' + self.name() + bar
		if self.distribution_packages():
			string += provided
			for (k, v) in self.distribution_packages().items(): string += bar + ' -> on ' + k + ' distributions, the package names are ' + v
		if self.url() is not None:
			if not self.distribution_packages(): string += provided
			string += bar + ' -> '
			if self.distribution_packages(): string += 'otherwise, '
			string += 'the source of this package can be downloaded from ' + self.url()
			from packageneric.generic.scons.tty_font import tty_font
			external_packages = filter(lambda x: isinstance(x, external_package) and not x.result(), self.dependencies())
			if len(external_packages):
				string += separator
				indent = bar + ' ' + tty_font('37')
				string += indent + 'which should bring indirect dependencies:'
				for external_package_ in external_packages:
					recursive = str(external_package_)
					if recursive[-1] == '\n': recursive = recursive[:-1]
					string += indent + recursive.replace('\n', indent) + tty_font()
		string += bar + line + '\n'
		return string
