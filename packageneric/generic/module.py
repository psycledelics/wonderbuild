# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006 johan boule <bohan@jabber.org>
# copyright 2006 psycledelics http://psycle.pastnotecut.org

import os

class module:
	class types:
		dynamic = 0
		shared = 1
		static = 2
		program = 3
		
	def __init__(
		self, 
		packageneric,
		source_package = None,
		name = None,
		version = None,
		description = '',
		depends = None,
		build_depends = None
	):
		self._packageneric = packageneric
		self._source_package = source_package
		self._name = name
		self._version = version
		self._description = description
		if depends is None: self._depends = []
		else: self._depends = depends
		if build_depends is None: self._build_depends = []
		else: self._build_depends = build_depends
		self._sources = []
		self._headers = []
		self._common_environment = None
		self._build_include_path = []
		self._build_defines = {}
		self._build_environment = None
		self._uninstalled_include_path = []
		self._uninstalled_defines = {}
		self._uninstalled_environment = None
		self._installed_include_path = []
		self._installed_defines = {}
		self._installed_environment = None
		self._targets = None
		self.packageneric().add_target(self)
	
	def packageneric(self): return self._packageneric
	
	def source_package(self): return self._source_package
	
	def name(self): return self._name
	
	def version(self): return self._version
	
	def description(self): return self._description
		
	def sources(self): return self._sources
	def add_source(self, source): self.sources().append(source)
	def add_sources(self, sources):
		for x in sources: self.add_source(x)
		
	def headers(self): return self._headers
	def add_header(self, header): self.headers().append(header)
	def add_headers(self, headers):
		for x in headers: self.add_header(x)
		
	def build_include_path(self): return self._build_include_path
	def add_build_include_path(self, path): self._build_include_path.append(path)
	
	def build_defines(self): return self._build_defines
	def add_build_define(self, name, value): self._build_defines[name] = value
		
	def uninstalled_include_path(self): return self._uninstalled_include_path
	def add_uninstalled_include_path(self, path): self._uninstalled_include_path.append(path)
	
	def uninstalled_defines(self): return self._uninstalled_defines
	def add_uninstalled_define(self, name, value): self._uninstalled_defines[name] = value
		
	def installed_include_path(self): return self._installed_include_path
	def add_installed_include_path(self, path): self._installed_include_path.append(path)
	
	def installed_defines(self): return self._installed_defines
	def add_installed_define(self, name, value): self._installed_defines[name] = value
		
	def build_depends(self):
		packages = []
		for package in self._build_depends:
			if not package in packages: packages.append(package)
			for package in package.depends():
				if not package in packages: packages.append(package)
		return packages
	def add_build_depend(self, build_depend): self._build_depends.append(build_depend)
	def add_build_depends(self, build_depends):
		for package in build_depends: self.add_build_depend(package)
		
	def depends(self):
		packages = []
		for package in self._depends:
			if not package in packages: packages.append(package)
			for package in package.depends():
				if not package in packages: packages.append(package)
		return packages
	def add_depend(self, depend): self._depends.append(depend)
	def add_depends(self, depends):
		for package in depends: self.add_depend(package)
		
	def _merge_common_environment_(self, destination):
		if not self._common_environment:
			self._common_environment = self.source_package()._common_environment_().Copy()
			depends_not_found = []
			for package in self.build_depends() + self.depends():
				if package.found(): package.merge_environment(self._common_environment)
				else: depends_not_found.append(str(package))
			if depends_not_found:
				message = "cannot build module '" + self.name() + "' because not all dependencies were found:"
				for depend_not_found in depends_not_found: message += str(depend_not_found)
				message += '\n'
				import os.path
				message += 'for details, see ' + os.path.join(self._common_environment.subst('$packageneric__build_directory'), 'configure.log')
				self.packageneric().abort(message)
		import packageneric.generic
		packageneric.generic._merge_environment(self._common_environment, destination)
	
	def build_environment(self):
		if not self._build_environment:
			self._build_environment = self.source_package().build_environment().Copy()
			self._merge_common_environment_(self._build_environment)
			self.add_build_include_path('packageneric/generic/detail/src') # todo for pre-compiled headers of std lib
			for i in self.build_include_path(): self._build_environment.AppendUnique(CPPPATH = [os.path.join(self.packageneric().build_directory(), i)])
			self._build_environment.AppendUnique(CPPPATH = self.build_include_path())
			self._build_environment.Append(CPPDEFINES = self.build_defines())
			self._build_environment.AppendUnique(CPPPATH = [os.path.join(self.packageneric().build_directory(), 'packageneric', 'modules', self.name(), 'src')])
			def namespaces():
				result = []
				for source in self.sources():
					# todo source.relative_path()
					import string, re
					result.append(re.sub('[^A-Z0-9_]', '_', string.upper(re.sub(os.path.sep, '__', os.path.splitext(source.relative())[0]))))
				return result
			import SCons.Node.Python
			self._build_environment.WriteToFile(
				os.path.join(self.packageneric().build_directory(), 'packageneric', 'modules', self.name(), 'src', 'packageneric', 'module.private.hpp'),
				SCons.Node.Python.Value(''.join(
					['#include <packageneric/source-package.private.hpp>\n'] +
					['#define PACKAGENERIC__MODULE__%s %s\n' % (n, v) for n, v in
						[
							('NAME', '"%s"' % self.name()),
							('VERSION',  '"%s"' % str(self.version()))
						] +
						[('SOURCE__%s' % n, '1') for n in namespaces()]
					]
				))
			)
			pkg_config = ''
			for package in self.build_depends() + self.depends():
				if package.pkg_config(): pkg_config += ' ' + package.pkg_config()
			if len(pkg_config): self._build_environment.ParseConfig('pkg-config --cflags --libs \'' + pkg_config + '\'')
		return self._build_environment
		
	def uninstalled_environment(self):
		if not self._uninstalled_environment:
			self._uninstalled_environment = self.source_package().uninstalled_environment().Copy()
			self._merge_common_environment_(self._uninstalled_environment)
			for i in self.uninstalled_include_path(): self._uninstalled_environment.AppendUnique(CPPPATH = [os.path.join(self.packageneric().build_directory(), i)])
			self._uninstalled_environment.AppendUnique(CPPPATH = self.uninstalled_include_path())
			self._uninstalled_environment.Append(CPPDEFINES = self.uninstalled_defines())
		return self._uninstalled_environment
				
	def merge_uninstalled_environment(self, destination):
		import packageneric.generic
		packageneric.generic._merge_environment(self.uninstalled_environment(), destination)
		
	def installed_environment(self):
		if not self._installed_environment:
			self._installed_environment = self.source_package().installed_environment().Copy()
			self._merge_common_environment_(self._installed_environment)
			self._installed_environment.AppendUnique(CPPPATH = self.installed_include_path())
			self._installed_environment.Append(CPPDEFINES = self.installed_defines())
		return self._installed_environment

	def merge_installed_environment(self, destination):
		import packageneric.generic
		packageneric.generic._merge_environment(self.installed_environment(), destination)

	def target_name(self): return 'lib' + self.name()
	
	def targets(self):
		if not self._targets:
			self.build_environment()
			self.uninstalled_environment()
			self.installed_environment()
			self._targets = [
				self.build_environment().SharedLibrary(os.path.join(self.packageneric().build_directory(), self.target_name()), [os.path.join(self.packageneric().build_directory(), x.full()) for x in self.sources()])
			]
		return self._targets
