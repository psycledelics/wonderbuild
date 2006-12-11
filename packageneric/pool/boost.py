# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006 johan boule <bohan@jabber.org>
# copyright 2006 psycledelics http://psycle.pastnotecut.org

from packageneric.generic.scons.check.external_package import external_package
from packageneric.generic.scons.check.cxx_build import cxx_build

class boost(external_package):
	def __init__(self, project, version_wanted_raw, libraries):
		self._version_wanted_raw = version_wanted_raw
		self._version_wanted_major = str(version_wanted_raw / 100000)
		self._version_wanted_minor = str(version_wanted_raw / 100 % 1000)
		self._version_wanted_patch = str(version_wanted_raw % 100)
		self._version_wanted = self._version_wanted_major + '.' + self._version_wanted_minor + '.' + self._version_wanted_patch
		self._libraries = libraries
		debian_packages = 'libboost-dev (>= %s)' % self._version_wanted
		for library in libraries: debian_packages += ', libboost-%s-dev (>= %s)' % (library, self._version_wanted)
		external_package.__init__(self, project,
			name = 'boost',
			dependencies = [],
			distribution_packages = {
				'debian and ubuntu': debian_packages,
				'gentoo': '...',
				'fedora': '...',
				'cygwin': 'boost-devel (>= %s)' % self._version_wanted
			},
			url = 'http://boost.org'
		)
	
	def dynamic_dependencies(self):
		source_texts = {}
		source_texts['version'] = \
			"""
				#include <boost/version.hpp>
				#if BOOST_VERSION < %i
					#error
				#endif
			""" % self._version_wanted_raw
		source_texts['signals'] = \
			"""
				#include <boost/signals/slot.hpp>
				void signals() { /* todo do something with it for a complete check */ }
			"""
		source_texts['thread'] = \
			"""
				#include <boost/thread/thread.hpp>
				void thread() { boost::thread::thread thread; }
			"""
		source_texts['filesystem'] = \
			"""
				#include <boost/filesystem/path.hpp>
				#include <boost/filesystem/operations.hpp>
				void filesystem() { boost::filesystem::path path(boost::filesystem::current_path()); }
			"""
		source_texts['serialization'] = \
			"""
				#include <boost/serialization/serialization.hpp>
				#include <boost/archive/basic_archive.hpp>
				void serialization() { /* todo do something with it for a complete check */ }
			"""
		source_texts['wserialization'] = \
			"""
				#include <boost/serialization/serialization.hpp>
				#include <boost/archive/basic_archive.hpp>
				void wserialization() { /* todo do something with it for a complete check */ }
			"""
		source_texts['iostream'] = \
			"""
				//#include <boost/...>
				void iostream() { /* todo do something with it for a complete check */ }
			"""
		source_texts['regex'] = \
			"""
				#include <boost/regex.hpp>
				void regex() { /* todo do something with it for a complete check */ }
			"""
		source_texts['program_options'] = \
			"""
				#include <boost/program_options.hpp>
				void program_options() { /* todo do something with it for a complete check */ }
			"""
		source_texts['python'] = \
			"""
				#include <boost/python.hpp>
				void python() { /* todo do something with it for a complete check */ }
			"""
		source_texts['date_time'] = \
			"""
				#include <boost/date_time/period.hpp>
				void date_time() { /* todo do something with it for a complete check */ }
			"""
		source_texts['unit_test_framework'] = \
			"""
				#include <boost/test/framework.hpp>
				void unit_test_framework() { /* todo do something with it for a complete check */ }
			"""
		source_texts['prg_exec_monitor'] = \
			"""
				#include <boost/test/execution_monitor.hpp>
				void prg_exec_monitor() { /* todo do something with it for a complete check */ }
			"""
		source_texts['test_exec_monitor'] = \
			"""
				#include <boost/test/execution_monitor.hpp>
				void test_exec_monitor() { /* todo do something with it for a complete check */ }
			"""

		# damn cygwin installs boost headers in e.g. /usr/include/boost-1_33_1/ and doesn't give symlinks for library files
		cxx_compiler_paths = []
		import os, os.path
		dir = os.path.join('/', 'usr', 'include')
		if os.path.isdir(dir):
			if not os.path.isdir(os.path.join(dir, 'boost')):
				for entry in os.listdir(dir):
					if entry.startswith('boost-'):
						path = os.path.join(dir, entry)
						self.project().trace('found boost headers in ' + path)
						if entry >= 'boost-' + self._version_wanted_major + '_' + self._version_wanted_minor + '_' + self._version_wanted_patch: # todo better version comparion
							self.project().trace('selecting boost headers in ' + path)
							cxx_compiler_paths = [path]
							break
		dir = os.path.join('/', 'usr', 'lib')
		libraries = self._libraries
		if os.path.isdir(dir):
			libraries = []
			for library in self._libraries:
				library_search = 'libboost_' + library + '-gcc-mt-s.a' # in e.g. cygwin. todo the version could even differ from the headers we selected above
				for entry in os.listdir(dir):
					if entry == library_search:
							self.project().trace('selecting boost library ' + os.path.join(dir, entry) + ' as name ' + library)
							library_search = library + '-gcc-mt-s'
							source_texts[library_search] = source_texts[library]
							library = library_search
							break
				libraries.append(library)

		all_in_one = cxx_build(self.project(),
			name = 'boost ' + ' '.join(libraries) + ' >= ' + self._version_wanted,
			cxx_compiler_paths = cxx_compiler_paths,
			libraries = ['boost_' + library for library in libraries],
			source_text = source_texts['version'] + '\n' + '\n'.join([source_texts[library] for library in libraries])
		)
		if all_in_one.result(): self.add_dependency(all_in_one)
		else: # report exactly what is missing
			checks = []
			checks.append(
				cxx_build(self.project(),
					name = 'boost version >= ' + self._version_wanted,
					cxx_compiler_paths = cxx_compiler_paths,
					source_text = source_texts['version']
				)
			)
			for library in libraries:
				checks.append(
					cxx_build(self.project(),
						name = 'boost ' + library,
						cxx_compiler_paths = cxx_compiler_paths,
						libraries = ['boost_' + library],
						source_text = source_texts[library]
					)
				)
			for check in checks:
				if not check.result(): self.add_dependency(check)
