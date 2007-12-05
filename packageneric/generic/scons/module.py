# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

import os
from projected import projected
from builder import builder

class module(projected, builder): # todo decide whether this can be derived from the node class too
	class target_types:
		loadable = 0
		shared = 1
		static = 2
		program = 3
		shared_but_pe = 4 # will be shared unless the platform uses pe executable format, in which case it will be static (windows dll needs import/export attributes on symbols)
		
	def __init__(
		self, 
		source_package,
		name,
		version = None,
		description = None,
		dependencies = None,
		build_dependencies = None,
		target_type = target_types.loadable
	):
		projected.__init__(self, source_package.project())
		builder.__init__(self, name)
		self._source_package = source_package
		self._version = version
		self._description = description

		if dependencies is None: self._dependencies = []
		else: self._dependencies = dependencies

		if build_dependencies is None: self._build_dependencies = []
		else: self._build_dependencies = build_dependencies

		self._target_type = target_type
		self.project().add_builder(self)
	
	def source_package(self): return self._source_package
	
	def version(self):
		if self._version is not None: return self._version
		return self.source_package().version()
	
	def description(self):
		if self._description is not None: return self._description
		return self.source_package().description()
		
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

	def build_immediate_dependencies(self): return self._build_dependencies
	
	def build_deep_dependencies(self):
		packages = []
		for package in self._build_dependencies:
			if not package in packages: packages.append(package)
			for package in package.dependencies():
				if not package in packages: packages.append(package)
		return packages
	def add_build_dependency(self, build_dependency): self._build_dependencies.append(build_dependency)
	def add_build_dependencies(self, build_dependencies):
		for package in build_dependencies: self.add_build_dependency(package)
	
	def immediate_dependencies(self): return self._dependencies
	
	def deep_dependencies(self):
		packages = []
		for package in self._dependencies:
			if not package in packages: packages.append(package)
			for package in package.dependencies():
				if not package in packages: packages.append(package)
		return packages
	def add_dependency(self, dependency): self._dependencies.append(dependency)
	def add_dependencies(self, dependencies):
		for package in dependencies: self.add_dependency(package)
	
	def dynamic_dependencies(self): pass # todo this is also a method of the node class
	
	def contexes(self):
		try: return self._contexes
		except AttributeError:
			self._contexes = self.source_package().contexes().attached()
			return self._contexes
			
	def alias_names(self): return ['packageneric:module', self.name()]
	
	def target_type(self): return self._target_type
	
	def targets(self): # todo to allow libraries to be built as several types at the same time, pass target_type here instead of in the constructor
		try: return self._targets
		except AttributeError:
			#import time ; t = time.time ; t0 = t()
			#print 'OOOOOOOOOOOOOOOOO'

			self.dynamic_dependencies() # todo this is also a method of the node class
			dependencies_not_found = []

			for package in self.build_immediate_dependencies():
				if package.result():
					package.targets()
					self.contexes().build().attach(package.output_env())
				else: dependencies_not_found.append(package)

			for package in self.immediate_dependencies():
				if package.result():
					package.targets()
					self.contexes().attach(package.output_env())
				else: dependencies_not_found.append(package)

			if dependencies_not_found:
				message = "cannot build module '" + self.name() + "' because not all dependencies were found:\n"
				for dependency_not_found in dependencies_not_found: message += str(dependency_not_found)
				message += '\n'
				message += 'for details, see ' + self.project().check_log()
				self.project().abort(message)

			dependencies = []
			for dependency_lists in [package.targets() for package in self.build_immediate_dependencies() + self.immediate_dependencies()]:
				for dependency_list in dependency_lists: dependencies.extend(dependency_list)

			# add include path for pre-compiled headers of std lib
			self.contexes().build().compilers().cxx().paths().add([os.path.join(self.project().packageneric_dir(), 'generic', 'scons', 'src')])

			# for each include path, we add the same path in the build dir
			# note that we could just use build dir paths only since scons makes the src path a vpath like make
			paths = []
			for path in self.contexes().source().compilers().cxx().paths(): paths.append(os.path.join(self.project().intermediate_target_dir(), path))
			for path in paths: self.contexes().source().compilers().cxx().paths().add(paths)

			# add include path for the module's autogenerated header
			self.contexes().build().compilers().cxx().paths().add([os.path.join(self.project().build_variant_intermediate_dir(), 'modules', self.name(), 'src')])

			scons = self.project()._scons().Copy() # .Clone()
			self.contexes().build()._scons(scons)
			
			def namespaces():
				result = []
				for source in self.sources():
					import re
					result.append(re.sub('[^A-Z0-9_]', '_', os.path.splitext(source.relative())[0].replace(os.path.sep, '__').upper()))
				return result
			scons.FileFromValue(
				os.path.join(self.project().build_variant_intermediate_dir(), 'modules', self.name(), 'src', 'packageneric', 'module.private.hpp'),
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
			
			target_type = self.target_type()
			if target_type == self.target_types.shared_but_pe:
				if self.project().platform_executable_format() == 'pe': target_type = self.target_types.static
				else: target_type = self.target_types.shared
			if self.target_type() == self.target_types.loadable: builder = scons.LoadableModule
			elif target_type == self.target_types.shared: builder = scons.SharedLibrary
			elif target_type == self.target_types.static: builder = scons.StaticLibrary
			elif self.target_type() == self.target_types.program: builder = scons.Program
			else: self.project().abort("unknown binary type for module '%s'" % self.name())
			if self.target_type() == self.target_types.program or \
				(target_type in (self.target_types.shared, self.target_types.loadable) and self.project().platform_executable_format() == 'pe'):
				destination = os.path.join('$packageneric__install__bin')
				# todo the .dll file needs to go to bin dir ; the .lib, .pdb, .exp still need to go to the lib dir (and .ilk kept in intermediate dir)
			else:
				destination = os.path.join('$packageneric__install__lib')
			self._targets = [
				builder(os.path.join('$packageneric__install__stage_destination', destination, self._target_name()), [os.path.join(self.project().intermediate_target_dir(), x.full()) for x in self.sources()])
			]
			for target_list in self._targets:
				for target in target_list:
					if self.target_type() == self.target_types.static: pass # target.set_precious() # update archives instead of recreating them from scratch
				target.add_dependency(dependencies)

			#print 'OOOOOOOOOOOOOOOOO', t() - t0
			
			self._contexes.client().linker().libraries().add([self.name()])
			# added *before* targets is called (or else targets isn't called!).
			# todo BUG this doesn't make it transitive!

			return self._targets

	def _target_name(self):
		scons = self.project()._scons()
		if self.target_type() == self.target_types.loadable: return self.name() + scons.subst('$LDMODULESUFFIX') # scons.subst('$LDMODULEPREFIX') + self.name() + scons.subst('$LDMODULESUFFIX')
		target_type = self.target_type()
		if target_type == self.target_types.shared_but_pe:
			if self.project().platform_executable_format() == 'pe': target_type = self.target_types.static
			else: target_type = self.target_types.shared
		if target_type == self.target_types.shared: return self.name() # scons.subst('$SHLIBPREFIX') + self.name() + scons.subst('$SHLIBSUFFIX')
		if target_type == self.target_types.static: return self.name() # scons.subst('$LIBPREFIX') + self.name() + scons.subst('$LIBSUFFIX')
		if self.target_type() == self.target_types.program: return self.name() + scons.subst('$PROGSUFFIX') # scons.subst('$PROGPREFIX') + self.name() + scons.subst('$PROGSUFFIX')
		else: self.project().abort("unknown binary type for module '%s'" % self.name())
	
