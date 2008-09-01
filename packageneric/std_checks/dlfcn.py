# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

from packageneric.generic.scons.check.external_package import external_package
from packageneric.generic.scons.check.cxx_build import cxx_build

class dlfcn(external_package):
	def __init__(self, project):
		external_package.__init__(self, project, name = 'posix dlfcn',
			url = 'http://google.ch posix 1003.1-2003',
			distribution_packages = {
				'debian and ubuntu': 'libc-dev (>= 0)',
				'gentoo': '...',
				'fedora': '...',
				'cygwin': 'cygwin (1.5.19)'
			},
			dependencies = []
		)
	
	def dynamic_dependencies(self):
		class build(cxx_build):
			def __init__(self, project, with_library):
				if with_library:
					name = 'dlfcn with dl library'
					libraries = ['dl']
				else:
					name = 'dlfcn without dl library'
					libraries = []
				cxx_build.__init__(self, project, name = name,
					dependencies = [],
					libraries = libraries,
					source_text = \
						"""\
							#include <dlfcn.h>
							void dlfcn()
							{
								void * lib(dlopen("lib", RTLD_LAZY));
								void * sym(dlsym(lib, "sym"));
								char * error(dlerror());
								int result(dlclose(lib));
							}
						"""
				)
		dependency_with = build(self.project(), True)
		if dependency_with.result(): self.add_dependency(dependency_with)
		else:
			dependency_without = build(self.project(), False)
			if dependency_without.result(): self.add_dependency(dependency_without)
			else: self.add_dependencies([dependency_with, dependency_without])
