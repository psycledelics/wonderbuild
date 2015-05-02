# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

from packageneric.scons.check.external_package import external_package
from packageneric.scons.check.cxx_build import cxx_build
from packageneric.scons.version import version

class gnug(external_package):
	def __init__(self, project):
		external_package.__init__(self, project,
			name = 'g++',
			dependencies = [],
			distribution_packages = {
				'debian and ubuntu': 'g++ (>= 0)',
				'gentoo': '...',
				'fedora': '...',
				'cygwin': 'gcc-g++ (>= 3.4.4-1)'
			},
			url = 'http://gcc.gnu.org'
		)
	
	def dynamic_dependencies(self):
		gnug4 = cxx_build(self.project(), name = 'gnug 4', source_text = \
			"""\
				#if __GNUG__ < 4
					#error this is not gcc g++ >= 4
				#endif
			\n""" # gcc -E -dM -std=c++98 -x c++-header /dev/null | sort
		)
		if gnug4.result():
			gnug = gnug3 = gnug4
			self._version = version(4)
		else:
			gnug3 = cxx_build(self.project(), name = 'gnug 3', source_text = \
				"""\
					#if __GNUG__ < 3
						#error this is not gcc g++ >= 3
					#endif
				\n""" # gcc -E -dM -std=c++98 -x c++-header /dev/null | sort
			)
			if gnug3.result():
				gnug = gnug3
				self._version = version(3)
			else:
				# We don't bother checking for older versions.
				# Instead we simply make it so the gnu g++ compiler is not detected at all,
				# and thus gnu-specific options will not be used at all.
				gnug = gnug3 # this has the effect that gnug.result() is False since we have gnu g++ < 3
		self.add_dependency(gnug)

	def version(self):
		try: return self._version
		except AttributeError:
			if not self.result(): self._version = version(-1)
			return self._version
		
	def mingw(self):
		try: return self._mingw
		except AttributeError:
			self._mingw = cxx_build(self.project(), name = 'mingw', dependencies = [self], source_text = \
				"""\
					#if !defined __MINGW64__ && !defined __MINGW32__
						#error this is not gcc mingw
					#endif
					#if !defined _WIN64 && !defined _WIN32
						#error mingw but not microsoft windows
					#endif
				\n""" # gcc (-mno-cygwin) -E -dM -std=c++98 -x c++-header /dev/null | sort
			)
			return self._mingw

	def elf(self):
		try: return self._elf
		except AttributeError:
			self._elf = cxx_build(self.project(), name = 'elf', dependencies = [self], source_text = \
				"""\
					#if !defined __ELF__
						#error the target platform is not elf
					#endif
				\n""" # gcc -E -dM -std=c++98 -x c++-header /dev/null | sort
			)
			return self._elf
