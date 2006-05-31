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
		for x in self.binary_packages():
			for xx in x.build_depends():
				if not xx in result:
					result.append(xx)
		return result
	
	def control(self):
		string = ''
		string += 'Source: ' + self.source_package().name() + '\n'
		string += 'Section: ' + self.section() + '\n'
		string += 'Priority: ' + self.priority() + '\n'
		string += 'Build-Depends: scons'
		for package in self.build_depends():
			string += ', ' + package
		string += '\n'
		if not self.maintainer() is None:
			string += 'Maintainer: ' + self.maintainer().name() + ' <' + self.maintainer().email() + '>\n'
		if len(self.uploaders()):
			string += 'Uploaders: '
			for x in self.uploaders():
				string += x.name() + ' <' + x.email() + '>, ' # use coerce
			string += '\n'
		string += 'Standards-Version: 3.6.2\n'
		for binary_package in self.binary_packages():
			string += '\n'
			string += 'Package: ' + binary_package.name() + '\n'
			if len(binary_package.provides()):
				string += 'Provides: '
				for provide in binary_package.provides():
					string += provide + ', '
				string += '\n'
			if len(binary_package.recommends()):
				string += 'Recommends: '
				for recommend in x.recommends():
					string += recommend + ', '
				string += '\n'
			if len(binary_package.suggests()):
				string += 'Suggests: '
				for suggest in binary_package.suggests():
					string += suggest + ', '
				string += '\n'
			string += 'Depends: ${shlibs:Depends}, ${misc:Depends}'
			for package in binary_package.depends():
				string += ', ' + package
			string += '\n'
			string += 'Section: '
			if binary_package.section() is None:
				string += self.section()
			else:
				string += binary_package.section()
			string += '\n'
			string += 'Architecture: ' + binary_package.architecture() + '\n'
			string += 'Description: ' + binary_package.description() + '\n '
			description = self.long_description() + '\n\n' + binary_package.long_description()
			was_new_line = False
			for char in description:
				if char == '\n':
					if was_new_line:
						string += '.'
					was_new_line = True
					string += '\n '
				else:
					was_new_line = False
					string += char
			string += '\n'
		return string
