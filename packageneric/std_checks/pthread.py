# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

from packageneric.scons.check.external_package import external_package
from packageneric.scons.check.cxx_build import cxx_build

class pthread(external_package):
	def __init__(self, project):
		external_package.__init__(self, project, name = 'posix thread',
			url = 'http://google.ch posix 1003.1-2003',
			distribution_packages = {
				'debian and ubuntu': 'libc-dev (>= 0)',
				'gentoo': '...',
				'fedora': '...',
				'cygwin': 'cygwin (1.5.19)'
			},
			dependencies = [
				cxx_build(project, name = 'pthread', libraries = ['pthread'], source_text = \
					"""\
						#include <pthread.h>
						void pthread()
						{
							pthread_t self(pthread_self());
						}
					"""
				)
			]
		)

	def output_env(self):
		try: return self._output_env
		except AttributeError:
			self._output_env = external_package.output_env(self)
			#if self.result():
			#	self.output_env()... compiler-specific
			return self._output_env
