# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006 johan boule <bohan@jabber.org>
# copyright 2006 psycledelics http://psycle.pastnotecut.org

from packageneric.generic.scons.check.external_package import external_package
from packageneric.generic.scons.check.cxx_build import cxx_build

class cmath(external_package):
	def __init__(self, project):
		external_package.__init__(self, project,
			name = 'cmath',
			dependencies = [],
			distribution_packages = {},
			url = None
		)
	
	def dynamic_dependencies(self):
		class build(cxx_build):
			def __init__(self, project, with_library):
				if with_library:
					name = 'cmath with m library'
					libraries = ['m']
				else:
					name = 'cmath without m library'
					libraries = []
				cxx_build.__init__(self, project, name = name, libraries = libraries,
					#dependencies = [cxx, std],
					source_text = \
						"""\
							#include <cmath>
							void cmath()
							{
								float f(std::sin(.0f));
								double d(std::sin(.0));
							}
						"""
				)
		dependency = build(self.project(), True)
		if dependency.result(): self.add_dependency(dependency)
		else: self.add_dependency(build(self.project(), False))
