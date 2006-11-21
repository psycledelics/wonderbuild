# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006 johan boule <bohan@jabber.org>
# copyright 2006 psycledelics http://psycle.pastnotecut.org

import os, os.path
from builder import builder

class module(builder):
	class target_types:
		loadable = 0
		shared = 1
		static = 2
		program = 3
		
	def __init__(
		self, 
		source_package,
		name,
		version,
		description,
		dependencies = None,
		build_dependencies = None,
		target_type = target_types.loadable # todo defer the decision about what type to build down to the targets() method
	):
		self._source_package = source_package
		self._name = name
		self._version = version
		self._description = description

		if dependencies is None: self._dependencies = []
		else: self._dependencies = dependencies

		if build_dependencies is None: self._build_dependencies = []
		else: self._build_dependencies = build_dependencies

		self._target_type = target_type
		self.project().add_builder(self)
	
	def project(self): return self.source_package().project()
	
	def source_package(self): return self._source_package
	
	def name(self): return self._name
	
	def version(self): return self._version
	
	def description(self): return self._description
		
	def sources(self):
		try: return self._sources
		except AttributeError:
			self._sources = []
		return self._sources
	def add_source(self, source): self.sources().append(source)
	def add_sources(self, sources):
		for x in sources: self.add_source(x)
		
	def headers(self):
		try: return self._headers
		except AttributeError:
			self._headers = []
			return self._headers
	def add_header(self, header): self.headers().append(header)
	def add_headers(self, headers):
		for x in headers: self.add_header(x)

	def build_dependencies(self):
		packages = []
		for package in self._build_dependencies:
			if not package in packages: packages.append(package)
			for package in package.dependencies():
				if not package in packages: packages.append(package)
		return packages
	def add_build_dependency(self, build_dependency): self._build_dependencies.append(build_dependency)
	def add_build_dependencies(self, build_dependencies):
		for package in build_dependencies: self.add_build_dependency(package)
		
	def dependencies(self):
		packages = []
		for package in self._dependencies:
			if not package in packages: packages.append(package)
			for package in package.dependencies():
				if not package in packages: packages.append(package)
		return packages
	def add_dependency(self, dependency): self._dependencies.append(dependency)
	def add_dependencies(self, dependencies):
		for package in dependencies: self.add_dependency(package)
	
	def target_type(self): return self._target_type
	
	def contexes(self):
		try: return self._contexes
		except AttributeError:
			self._contexes = self.source_package().contexes().attached()
			dependencies_not_found = []
			for package in self.build_dependencies() + self.dependencies():
				if package.result(): self._contexes.build().attach(package.output_env())
				else: dependencies_not_found.append(package)
			if dependencies_not_found:
				message = "cannot build module '" + self.name() + "' because not all dependencies were found:"
				for dependency_not_found in dependencies_not_found: message += str(dependency_not_found)
				message += '\n'
				message += 'for details, see ' + os.path.join(self.project()._scons().subst('$packageneric__build_directory'), 'configure.log')
				self.project().abort(message)
			return self._contexes
			
	def alias_names(self): return ['packageneric:module', self.name()]
	
	def target_name(self):
		scons = self.project()._scons()
		if self.target_type() == self.target_types.loadable: return self.name() # scons.subst('$LDMODULEPREFIX') + self.name() + scons.subst('$LDMODULESUFFIX')
		if self.target_type() == self.target_types.shared: return self.name() # scons.subst('$SHLIBPREFIX') + self.name() + scons.subst('$SHLIBSUFFIX')
		if self.target_type() == self.target_types.static: return self.name() # scons.subst('$LIBPREFIX') + self.name() + scons.subst('$LIBSUFFIX')
		elif self.target_type() == self.target_types.program: return self.name() # scons.subst('$PROGPREFIX') + self.name() + scons.subst('$PROGSUFFIX')
		else: self.project().abort("unknown binary type for module '%s'" % self.name())
	
	def targets(self, target_type = target_types.loadable):
		try: return self._targets
		except AttributeError:
			dependencies = []
			for dependency_lists in [package.targets() for package in self.build_dependencies() + self.dependencies()]:
				for dependency_list in dependency_lists: dependencies.extend(dependency_list)

			self.contexes().build().compilers().cxx().paths().add([os.path.join('packageneric', 'generic', 'detail', 'src')]) # for pre-compiled headers of std lib

			for context in self.contexes().build(), self.contexes().client().uninstalled():
				paths = []
				for path in context.compilers().cxx().paths(): paths.append(path)
				for path in paths: context.compilers().cxx().paths().add([os.path.join(self.project().build_directory(), path)])

			self.contexes().build().compilers().cxx().paths().add([os.path.join(self.project().build_directory(), 'packageneric', 'modules', self.name(), 'src')])

			scons = self.project()._scons().Copy()
			self.contexes().build()._scons(scons)

			import check.pkg_config
			pkg_config = filter(lambda x: isinstance(x, check.pkg_config.pkg_config), self.build_dependencies() + self.dependencies())
			if len(pkg_config):
				pkg_config = ' '.join([pkg_config.name() for pkg_config in pkg_config])
				save = os.environ.get('PKG_CONFIG_PATH', '')
				if save: os.environ['PKG_CONFIG_PATH'] = self.contexes().build().os_env()['PKG_CONFIG_PATH'] # todo append with os_env().add_inerited(['PKG_CONFIG_PATH'])
				try:
					if self.target_type() == self.target_types.program: static = ' --static'
					else: static = ''
					scons.ParseConfig('pkg-config --cflags --libs ' + static + '\'' + pkg_config + '\'')
				finally:
					if save: os.environ['PKG_CONFIG_PATH'] = save

			def namespaces():
				result = []
				for source in self.sources():
					import string, re
					result.append(re.sub('[^A-Z0-9_]', '_', string.upper(re.sub(os.path.sep, '__', os.path.splitext(source.relative())[0]))))
				return result
			scons.FileFromValue(
				os.path.join(self.project().build_directory(), 'packageneric', 'modules', self.name(), 'src', 'packageneric', 'module.private.hpp'),
				''.join(
					['#include <packageneric/source-package.private.hpp>\n'] +
					['#define PACKAGENERIC__MODULE__%s %s\n' % (n, v) for n, v in
						[
							('NAME', '"%s"' % self.name()),
							('VERSION',  '"%s"' % str(self.version()))
						] +
						[('SOURCE__%s' % n, '1') for n in namespaces()]
					]
				)
			)
			
			if self.target_type() == self.target_types.loadable: builder = scons.LoadableModule
			elif self.target_type() == self.target_types.shared: builder = scons.SharedLibrary
			elif self.target_type() == self.target_types.static: builder = scons.StaticLibrary
			elif self.target_type() == self.target_types.program: builder = scons.Program
			else: self.project().abort("unknown binary type for module '%s'" % self.name())
			self._targets = [
				builder(os.path.join(self.project().build_directory(), self.target_name()), [os.path.join(self.project().build_directory(), x.full()) for x in self.sources()])
			]
			for target_list in self._targets:
				for target in target_list:
					if self.target_type() == self.target_types.static: pass # target.set_precious() # update archives instead of recreating them from scratch
					target.add_dependency(dependencies)
			return self._targets
