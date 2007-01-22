# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

from packageneric.generic.scons.check.external_package import external_package

class microsoft_windows(external_package):
	def __init__(self, project):
		external_package.__init__(self, project, name = 'microsoft windows api',
			url = 'http://msdn.microsoft.com',
			distribution_packages = {'microsoft (maybe windows updates?)': 'windows platform sdk'},
			dependencies = [
			]
		)

	def dynamic_dependencies(self):
		from packageneric.generic.scons.check.cxx_build import cxx_build
		self.add_dependency(
			cxx_build(self.project(), name = 'microsoft windows api', libraries = [], source_text = \
				"""\
					#if !defined _WIN64 && !defined _WIN32
						#error Bill Gates: No such fool or dictatory
					#endif
					#if !defined _WIN64
						#define WINVER 0x510
						#define _WIN32_WINDOWS WINVER
						#define _WIN32_NT WINVER
						#define _WIN32_IE 0x600
						//#define WIN32_LEAN_AND_MEAN
						//#define WIN32_EXTRA_LEAN
					#endif
					//#define VC_EXTRA_LEAN
					#define NOMINMAX
					#include <windows.h>
					#if !defined _WINDOWS_ && !defined __GNUG__ // hmm, mingw's header is bizarre
						#error bad windows header
					#endif
					#if defined min || defined max
						#error bad windows header: clash with standard library
					#endif
					void microsoft_windows()
					{
						// todo do something with it for a complete check
						#if 0 // <wincon.h>
							GetConsoleWindow();
						#endif
					}
				"""
			)
		)
