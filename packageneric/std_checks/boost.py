# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

from packageneric.scons.check.external_package import external_package
from packageneric.scons.check.cxx_build import cxx_build
from stdcxx import stdcxx

class boost(external_package):
	def __init__(self, project, version_wanted_raw, libraries):
		self._version_wanted_raw = version_wanted_raw
		self._version_wanted_major = str(version_wanted_raw / 100000)
		self._version_wanted_minor = str(version_wanted_raw / 100 % 1000)
		self._version_wanted_patch = str(version_wanted_raw % 100)
		self._version_wanted = self._version_wanted_major + '.' + self._version_wanted_minor + '.' + self._version_wanted_patch
		self._libraries = libraries

		debian_packages = 'libboost-dev (>= %s)' % self._version_wanted
		for library in libraries:
			name = library
			if name in ['unit_test_framework', 'test_exec_monitor', 'prg_exec_monitor']: name = 'test'
			debian_packages += ', libboost-%s-dev (>= %s)' % (name, self._version_wanted)

		external_package.__init__(self, project, name = 'boost ' + ' '.join(libraries),
			url = 'http://boost.org',
			distribution_packages = {
				'debian and ubuntu': debian_packages,
				'gentoo': '...',
				'fedora': '...',
				'cygwin': 'boost-devel (>= %s)' % self._version_wanted
			},
			dependencies = [stdcxx(project)]
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
		def auto_link(name, dynamic = True):
			result = \
				"""
					#define BOOST_LIB_NAME boost_%s
				""" % name
			if dynamic: result += \
				"""
					#if defined _DLL || defined _RTLDLL // as tested in <boost/config/auto_link.hpp>
						#define BOOST_DYN_LINK
					#endif
				"""
			result += \
				"""
					#define BOOST_LIB_DIAGNOSTIC
					#include <boost/config/auto_link.hpp>
				"""
			return result
		source_texts['signals'] = \
			"""
				#include <boost/signals/slot.hpp>
				void signals() { /* todo do something with it for a complete check */ }
			""" + auto_link('signals')
		source_texts['thread'] = \
			"""
				#include <boost/thread/thread.hpp>
				void thread() { boost::thread thread; }
			""" + auto_link('thread')
		source_texts['filesystem'] = \
			"""
				#include <boost/filesystem/path.hpp>
				#include <boost/filesystem/operations.hpp>
				void filesystem() { boost::filesystem::path path(boost::filesystem::current_path()); }
			""" + auto_link('filesystem')
		source_texts['serialization'] = \
			"""
				#include <boost/serialization/serialization.hpp>
				#include <boost/archive/basic_archive.hpp>
				void serialization() { /* todo do something with it for a complete check */ }
			""" + auto_link('serialization')
		source_texts['wserialization'] = \
			"""
				#include <boost/serialization/serialization.hpp>
				#include <boost/archive/basic_archive.hpp>
				void wserialization() { /* todo do something with it for a complete check */ }
			""" + auto_link('wserialization')
		source_texts['iostream'] = \
			"""
				//#include <boost/...>
				void iostream() { /* todo do something with it for a complete check */ }
			""" + auto_link('iostream')
		source_texts['regex'] = \
			"""
				#include <boost/regex.hpp>
				void regex() { /* todo do something with it for a complete check */ }
			""" + auto_link('regex')
		source_texts['program_options'] = \
			"""
				#include <boost/program_options.hpp>
				void program_options() { /* todo do something with it for a complete check */ }
			""" + auto_link('program_options')
		source_texts['python'] = \
			"""
				#include <boost/python.hpp>
				void python() { /* todo do something with it for a complete check */ }
			""" + auto_link('python')
		source_texts['date_time'] = \
			"""
				#include <boost/date_time/period.hpp>
				void date_time() { /* todo do something with it for a complete check */ }
			""" + auto_link('date_time')
		source_texts['unit_test_framework'] = \
			"""
				#include <boost/test/framework.hpp>
				void unit_test_framework() { /* todo do something with it for a complete check */ }
			""" + auto_link('unit_test_framework', dynamic = False)
		source_texts['prg_exec_monitor'] = \
			"""
				#include <boost/test/execution_monitor.hpp>
				void prg_exec_monitor() { /* todo do something with it for a complete check */ }
			""" + auto_link('prg_exec_monitor', dynamic = False)
		source_texts['test_exec_monitor'] = \
			"""
				#include <boost/test/execution_monitor.hpp>
				void test_exec_monitor() { /* todo do something with it for a complete check */ }
			""" + auto_link('test_exec_monitor', dynamic = False)
		source_texts['wave'] = \
			"""
				#include <boost/wave/wave_version.hpp>
				void wave() { /* todo do something with it for a complete check */ }
			""" + auto_link('wave', dynamic = False)

		cxx_compiler_paths = []
		libraries = self._libraries[:]

		if self.project().platform() == 'posix':
			for library in self._libraries:
				library_select = library + '-mt'
				source_texts[library_select] = source_texts[library]
				libraries.remove(library)
				libraries.append(library_select)
		elif self.project().platform() == 'cygwin': # todo and no -mno-cygwin passed to the compiler
			# damn cygwin installs boost headers in e.g. /usr/include/boost-1_33_1/ and doesn't give symlinks for library files
			import os
			dir = os.path.join(os.path.sep, 'usr', 'include')
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
			dir = os.path.join(os.path.sep, 'usr', 'lib')
			if os.path.isdir(dir):
				dir_list = os.listdir(dir)
				libraries = self._libraries[:]
				for library in self._libraries:
					library_select = library + '-gcc-mt-s' # in e.g. cygwin, always static :-(. todo the version could even differ from the headers we selected above
					library_search = 'libboost_' + library_select + '.a' # in e.g. cygwin, always static :-( but if there's also a .dll.a, the linker will still pick it :)
					if library_search in dir_list:
						self.project().trace('selecting boost library ' + library_select + ' as name ' + library + ' (found ' + os.path.join(dir, library_search) + ')')
						source_texts[library_select] = source_texts[library]
						libraries.remove(library)
						libraries.append(library_select)

		link_libraries = libraries
		
		if cxx_build(self.project(), name = 'auto link',
			cxx_compiler_paths = cxx_compiler_paths,
			source_text = \
				"""
					// text below copied from <boost/config/auto_link.hpp>
					#include <boost/config.hpp>
					#if \\
						!( \\
							defined(BOOST_MSVC) || \\
							defined(__BORLANDC__) || \\
							(defined(__MWERKS__) && defined(_WIN32) && (__MWERKS__ >= 0x3000)) || \\
							(defined(__ICL) && defined(_MSC_EXTENSIONS) && (_MSC_VER >= 1200)) \\
						)
						#error no auto link
					#endif
				"""
		).result(): link_libraries = []

		def make_all_in_one():
			return cxx_build(self.project(),
				name = 'boost ' + ' '.join(link_libraries) + ' >= ' + self._version_wanted,
				cxx_compiler_paths = cxx_compiler_paths,
				libraries = ['boost_' + library for library in link_libraries],
				source_text = source_texts['version'] + '\n' + '\n'.join([source_texts[library] for library in link_libraries])
			)

		all_in_one = make_all_in_one()
		if all_in_one.result():
			self.add_dependency(all_in_one)
			return
			
		if self.project().platform() == 'posix':
			link_libraries = self._libraries
			all_in_one = make_all_in_one()
			if all_in_one.result():
				self.add_dependency(all_in_one)
				return
				
		# report exactly what is missing
		checks = []
		checks.append(
			cxx_build(self.project(), name = 'boost version >= ' + self._version_wanted,
				cxx_compiler_paths = cxx_compiler_paths,
				source_text = source_texts['version']
			)
		)
		for library in libraries:
			if len(link_libraries): link_library = ['boost_' + library]
			else: link_library = [] # todo cygwin
			checks.append(
				cxx_build(self.project(), name = 'boost ' + library,
					cxx_compiler_paths = cxx_compiler_paths,
					libraries = link_library,
					source_text = source_texts[library]
				)
			)
		for check in checks:
			if not check.result(): self.add_dependency(check)
