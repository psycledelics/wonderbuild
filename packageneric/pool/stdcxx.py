# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006 johan boule <bohan@jabber.org>
# copyright 2006 psycledelics http://psycle.pastnotecut.org

from packageneric.generic.scons.check.external_package import external_package
from packageneric.generic.scons.check.cxx_build import cxx_build

class stdcxx(external_package):
	def __init__(self, project):
		from cmath import cmath
		external_package.__init__(self, project,
			name = 'stdc++',
			dependencies = [cmath(project)],
			distribution_packages = {
				'debian and ubuntu': 'libstdc++-dev (>= 0)',
				'gentoo': '...',
				'fedora': '...',
				'cygwin': 'gcc-g++ (>= 3.4.4-1)'
			},
			url = 'http://google.ch iso c++'
		)
	
	def dynamic_dependencies(self):
		all_in_one = cxx_build(self.project(),
			name = 'stdc++',
			dependencies = [],
			libraries = [],
			source_text = \
				"""\
					#if !defined __cplusplus
						#error not a c++ compiler
					#endif
					
					#if !defined __STDC__
						#error no standard library
					#endif
					
					//#include <cstdint>
					//void cstdint() { std::int32_t i; }
					
					#include <stdint.h>
					#include <inttypes.h>
					void stdint() { int32_t i; }
				"""
		)
		self.add_dependency(all_in_one)
		if not all_in_one.result(): # report exactly what is missing
			cxx_build(self.project(), name = 'c++', source_text = \
				"""\
					#if !defined __cplusplus
						#error not a c++ compiler
					#endif
				"""
			).result()
			cxx_build(self.project(), name = 'std', source_text = \
				"""\
					#if !defined __STDC__
						#error no standard library
					#endif
				"""
			).result()
			cxx_build(self.project(), name = 'cstdint', source_text = \
				"""\
					#include <cstdint>
					void cstdint() { std::int32_t i; }
				"""
			).result()
			cxx_build(self.project(), name = 'stdint', source_text = \
				"""\
					#include <stdint.h>
					void stdint() { int32_t i; }
				"""
			).result()
			cxx_build(self.project(), name = 'inttypes', source_text = \
				"""\
					#include <inttypes.h>
					void inttypes() { int32_t i; }
				"""
			).result()
