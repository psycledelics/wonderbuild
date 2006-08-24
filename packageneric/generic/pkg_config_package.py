# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006 johan boule <bohan@jabber.org>
# copyright 2006 psycledelics http://psycle.pastnotecut.org

class pkg_config_package:
	def __init__(
		self,
		packageneric,
		name = None,
		version = None,
		description = '',
		modules = None
	):
		self._packageneric = packageneric
		self._name = name
		self._version = version
		self._description = description
		if modules is None:
			self._modules = []
		else:
			self._modules = modules
		
	def packageneric(self):
		return self._packageneric
		
	def name(self):
		return self._name
		
	def version(self):
		return self._version
	
	def description(self):
		return self._description
		
	def modules(self):
		return self._modules
		
	def build_depends(self):
		packages = []
		for module in self.modules():
			for package in module.build_depends() + module.depends():
				if not package in packages:
					packages.append(package)
		return packages

	def pc(self):
		string = 'prefix=' + self.packageneric().environment().subst('$packageneric__install_prefix') + '\n'
		string += 'Name: ' + self.name() + ' ' + str(self.version()) + '\n'
		string += 'Description: ' + self.description() + '\n'
		string += 'Version: ' + str(self.version()) + '\n' # todo module *interface* version, not package one
		string += 'CFlags: ' + self.packageneric().environment().subst('$CXXFLAGS') + '\n'
		string += 'Libs: ' + self.packageneric().environment().subst('$LINKFLAGS')
		for library in self.packageneric().environment().Split(self.packageneric().environment().subst('$LIBS')):
			string += ' -l' + library
		string += '\n'
		string += 'Libs.private: ' + '\n'
		string += 'Requires: '
		for package in self.build_depends():
			if package.pkg_config():
				string += package.pkg_config() + ' '
		string += '\n'
		#self.packageneric().environment().Alias(self.name() + '.pc', ...)
		return string
