# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

import os
from projected import projected
from named import named

class source_package(projected, named):
	def __init__(self, project,
		name = None,
		version = None,
		description = None,
		long_description = None,
		description_file = None,
		path = ''
	):
		projected.__init__(self, project)
		named.__init__(self, name)
		self._version = version
		if description_file is None:
			assert description is not None
			assert long_description is not None
			self._description = description
			self._long_description = long_description
		else:
			if description is not None or long_description is not None: project.warning('ignoring description parameters for source_package ' + name + ' because a description file was given.')
			description_file = file(description_file)
			self._description = description_file.readline()
			description_file.readline()
			self._long_description = description_file.read()
			description_file.close()
		self._path = path
		self._files = []
	
	def project(self): return self._project
	
	def name(self): return self._name
		
	def version(self): return self._version
		
	def description(self): return self._description
		
	def long_description(self): return self._long_description

	def contexes(self):
		try: return self._contexes
		except AttributeError:
			self._contexes = self.project().contexes().attached()
			env = self._contexes.build()
			env.compilers().cxx().paths().add([os.path.join(self.project().build_variant_intermediate_dir(), 'source-packages', self.name(), 'src')])
			self.project().file_from_value(
				os.path.join('source-packages', self.name(), 'src', 'packageneric', 'source-package.private.hpp'),
				''.join(
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
				)
			)
			return self._contexes
			
	def path(self): return self._path

	def add_files(self, files): self._files.extend(files)
