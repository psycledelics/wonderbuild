# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

class debian_package:
	def __init__(self, project,
		source_package = None, 
		name = None, 
		section = None, 
		architecture = 'any', 
		description = '', 
		long_description = ''
	):
		self._project = project
		self._source_package = source_package
		self._name = name
		if section is None: self._section = self.source_package().section()
		else: self._section = section
		self._architecture = architecture
		self._provides = []
		self._build_depends = []
		self._depends = []
		self._recommends = []
		self._suggests = []
		self._description = description
		self._long_description = long_description
		self._files = []
		
	def project(self): return self._project
		
	def source_package(self): return self._source_package
	
	def debian(self): return self.name() + ' (= ${Source-Version})'
		
	def distribution_packages(self): return {'debian': self.debian()}
	
	def name(self): return self._name
		
	def section(self): return self._section
		
	def architecture(self): return self._architecture
	
	def provides(self): return self._provides
	
	def	build_depends(self):
		packages = []
		for package in self._build_depends:
			if not package in packages: packages.append(package)
		return packages
	def add_build_depend(self, build_depend): self._build_depends.append(build_depend)
	def add_build_depends(self, build_depends):
		for package in build_depends: self.add_build_depend(package)
		
	def depends(self):
		packages = []
		for package in self._depends:
			if not package in packages: packages.append(package)
		return packages
	def add_depend(self, depend): self._depends.append(depend)
	def add_depends(self, depends):
		for package in depends: self.add_depend(package)
	
	def recommends(self): return self._recommends
		
	def suggests(self): return self._suggests
	
	def description(self): return self._description
		
	def long_description(self): return self._long_description
