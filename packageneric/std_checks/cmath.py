# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

from packageneric.scons.check.external_package import external_package
from packageneric.scons.check.cxx_build import cxx_build

class cmath(external_package):
	def __init__(self, project):
		external_package.__init__(self, project, name = 'iso standard c++ cmath library',
			url = 'http://google.ch iso c++',
			distribution_packages = {
				'debian and ubuntu': 'libstdc++-dev (>= 0)',
				'gentoo': '...',
				'fedora': '...',
				'cygwin': 'gcc-g++ (>= 3.4.4-1)'
			},
			dependencies = []
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
				cxx_build.__init__(self, project, name = name,
					dependencies = [], # [cxx, std],
					libraries = libraries,
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

		dependency_with = build(self.project(), True)
		if dependency_with.result(): self.add_dependency(dependency_with)
		else:
			dependency_without = build(self.project(), False)
			if dependency_without.result(): self.add_dependency(dependency_without)
			else: self.add_dependencies([dependency_with, dependency_without])
