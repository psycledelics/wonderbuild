# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006 johan boule <bohan@jabber.org>
# copyright 2006 psycledelics http://psycle.pastnotecut.org

import os.path

class source_package:
	def __init__(
		self,
		packageneric,
		name = None,
		version = None,
		description = '',
		long_description = '',
		path = ''
	):
		self._packageneric = packageneric
		self._name = name
		self._version = version
		self._description= description
		self._long_description = long_description
		self._path = path
	
	def packageneric(self): return self._packageneric
	
	def name(self): return self._name
		
	def version(self): return self._version
		
	def description(self): return self._description
		
	def long_description(self): return self._long_description

	def _common_environment_(self):
		try: return self._common_environment
		except AttributeError:
			self._common_environment = self.packageneric().common_environment().Copy()
			return self._common_environment
			
	def build_environment(self):
		try: return self._build_environment
		except AttributeError:
			self._build_environment = self.packageneric().build_environment().Copy()
			self._build_environment.Append(CPPPATH = [os.path.join(self.packageneric().build_directory(), 'packageneric', 'source-packages', self.name(), 'src')])
			import SCons.Node.Python
			self._build_environment.WriteToFile(
				os.path.join(self.packageneric().build_directory(), 'packageneric', 'source-packages', self.name(), 'src', 'packageneric', 'source-package.private.hpp'),
				SCons.Node.Python.Value(''.join(
						['#include <packageneric/configuration.private.hpp>\n'] +
						['#define PACKAGENERIC__PACKAGE__%s %s\n' % (n, v) for n, v in
							[	('NAME', '"%s"' % self.name()),
								('VERSION', '"%s"' % str(self.version()))
							] +
							[('VERSION__%s' % n, str(v)) for n, v in
								('MAJOR', self.version().major()),
								('MINOR', self.version().minor()),
								('PATCH', self.version().patch())
							]
						]
				))
			)
			return self._build_environment
		
	def uninstalled_environment(self):
		try: return self._uninstalled_environment
		except AttributeError:
			self._uninstalled_environment = self.packageneric().uninstalled_environment().Copy()
			return self._uninstalled_environment

	def installed_environment(self):
		try: return self._installed_environment
		except AttributeError:
			self._installed_environment = self.packageneric().installed_environment().Copy()
			return self._installed_environment

	def path(self): return self._path
