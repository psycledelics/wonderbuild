# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006 johan boule <bohan@jabber.org>
# copyright 2006 psycledelics http://psycle.pastnotecut.org

import os.path

class debian:
	def __init__(
		self,
		packageneric,
		source_package = None, 
		section = 'libs', 
		priority = 'optional',
		maintainer = '',
		uploaders = None,
		description = None,
		long_description = None,
		binary_packages = None,
		build_depends = None
	):
		self._packageneric = packageneric
		self._source_package = source_package
		self._section = section
		self._priority = priority
		self._maintainer = maintainer
		if uploaders is None:
			self._uploaders = []
		else:
			self._uploaders = uploaders
		if description is None and not source_package is None:
			self._description = source_package.description()
		else:
			self._description = description
		if long_description is None and not source_package is None:
			self._long_description = source_package.long_description()
		else:
			self._description = description
		if binary_packages is None:
			self._binary_packages = []
		else:
			self._binary_packages = binary_packages
		if build_depends is None:
			self._build_depends = []
		else:
			self._build_depends = build_depends
		self._control = None
		self._targets = None
		self.packageneric().add_builder(self)

	def packageneric(self):
		return self._packageneric
		
	def source_package(self):
		return self._source_package
		
	def section(self):
		return self._section
		
	def priority(self):
		return self._priority
		
	def maintainer(self):
		return self._maintainer
		
	def uploaders(self):
		return self._uploaders
		
	def description(self):
		return self._description
		
	def long_description(self):
		return self._long_description
		
	def binary_packages(self):
		return self._binary_packages
		
	def	build_depends(self):
		result = self._build_depends
		for binary_package in self.binary_packages():
			for package in binary_package.build_depends():
				if not package in result:
					result.append(package)
		return result
	
	def control(self):
		if self._control is None:
			string = ''
			string += 'Source: ' + self.source_package().name() + '\n'
			string += 'Section: ' + self.section() + '\n'
			string += 'Priority: ' + self.priority() + '\n'
			string += 'Build-Depends: scons'
			for package in self.build_depends():
				if package.distribution_packages().has_key('debian'): string += ', ' + package.distribution_packages()['debian']
			string += '\n'
			if not self.maintainer() is None: string += 'Maintainer: ' + self.maintainer().name() + ' <' + self.maintainer().email() + '>\n'
			if len(self.uploaders()):
				string += 'Uploaders: '
				for x in self.uploaders(): string += x.name() + ' <' + x.email() + '>, ' # use coerce
				string += '\n'
			string += 'Standards-Version: 3.6.2\n'
			for binary_package in self.binary_packages():
				string += '\n'
				string += 'Package: ' + binary_package.name() + '\n'
				if len(binary_package.provides()):
					string += 'Provides: '
					for provide in binary_package.provides(): string += provide + ', '
					string += '\n'
				if len(binary_package.recommends()):
					string += 'Recommends: '
					for recommend in x.recommends(): string += recommend + ', '
					string += '\n'
				if len(binary_package.suggests()):
					string += 'Suggests: '
					for suggest in binary_package.suggests(): string += suggest + ', '
					string += '\n'
				string += 'Depends: ${shlibs:Depends}, ${misc:Depends}'
				for package in binary_package.depends():
					if package.distribution_packages().has_key('debian'): string += ', ' + package.distribution_packages()['debian']
				string += '\n'
				string += 'Section: '
				if binary_package.section() is None: string += self.section()
				else: string += binary_package.section()
				string += '\n'
				string += 'Architecture: ' + binary_package.architecture() + '\n'
				string += 'Description: ' + binary_package.description() + '\n '
				description = self.long_description() + '\n\n' + binary_package.long_description()
				was_new_line = False
				for char in description:
					if char == '\n':
						if was_new_line: string += '.'
						was_new_line = True
						string += '\n '
					else:
						was_new_line = False
						string += char
				string += '\n'
			self._control = string
		return self._control

	def target_name(self): return 'debian'
		
	def targets(self):
		if not self._targets:
			import SCons.Node.Python
			self._targets = [
				self.packageneric().installed_environment().WriteToFile(os.path.join(self.packageneric().build_directory(), 'debian', 'control'), SCons.Node.Python.Value(self.control()))
			]
		return self._targets
