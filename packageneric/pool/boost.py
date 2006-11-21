# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006 johan boule <bohan@jabber.org>
# copyright 2006 psycledelics http://psycle.pastnotecut.org

from packageneric.generic.scons.check.external_package import external_package
from packageneric.generic.scons.check.cxx_build import cxx_build

class boost(external_package):
	def __init__(self, project, version_wanted_raw, libraries):
		self._version_wanted_raw = version_wanted_raw
		self._version_wanted = str(version_wanted_raw / 100000) + '.' + str(version_wanted_raw / 100 % 1000) + '.' + str(version_wanted_raw % 100)
		self._libraries = libraries
		debian_packages = 'libboost-dev (>= %s)' % self._version_wanted
		for library in libraries: debian_packages += ', libboost-%s-dev (>= %s)' % (library, self._version_wanted)
		external_package.__init__(self, project,
			name = 'boost',
			dependencies = [],
			distribution_packages = {
				'debian': debian_packages,
				'cygwin': 'boost-devel-1.33.1-2'
			},
			url = 'http://boost.org'
		)
	
	def dynamic_dependencies(self):
		all_in_one = cxx_build(self.project(),
			name = 'boost ' + ' '.join(self._libraries) + ' >= ' + self._version_wanted,
			libraries = ['boost_' + library for library in self._libraries],
			source_text = \
				"""\
					#include <boost/version.hpp>
					#if BOOST_VERSION < %i
						#error
					#endif
					#include <boost/thread/thread.hpp>
					void thread() { boost::thread::thread thread; }
					#include <boost/filesystem/path.hpp>
					#include <boost/filesystem/operations.hpp>
					void filesystem() { boost::filesystem::path path(boost::filesystem::current_path()); }
				""" % self._version_wanted_raw
		)
		self.add_dependency(all_in_one)
		if not all_in_one.result(): # report exactly what is missing
			cxx_build(self.project(), name = 'boost version >= ' + self._version_wanted, source_text = \
				"""\
					#include <boost/version.hpp>
					#if BOOST_VERSION < %i
						#error
					#endif
				""" % self._version_wanted_raw
			).result()
			for library in self._libraries:
				if library == 'thread':
					cxx_build(self.project(), name = 'boost thread', libraries = ['boost_thread'], source_text = \
						"""\
							#include <boost/thread/thread.hpp>
							void thread() { boost::thread::thread thread; }
						"""
					).result()
				if library == 'filesystem':
					cxx_build(self.project(), name = 'boost filesystem', libraries = ['boost_filesystem'], source_text = \
						"""\
							#include <boost/filesystem/path.hpp>
							#include <boost/filesystem/operations.hpp>
							void filesystem() { boost::filesystem::path path(boost::filesystem::current_path()); }
						"""
					).result()
