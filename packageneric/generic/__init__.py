#! /usr/bin/env python

# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006 johan boule <bohan@jabber.org>
# copyright 2006 psycledelics http://psycle.pastnotecut.org

import sys, os.path, fnmatch

if False:
	SetOption('implicit_cache', True)
	SourceSignatures('MD5') ('timestamp')
	TargetSignatures('build') ('content')

#@staticmethod
def _pkg_config(context, packageneric, name, what):
	command = 'pkg-config --%s \'%s\'' % (what, name)
	#packageneric.trace('checking for ' + command + ' ... ')
	context.Message('checking for ' + command + ' ... ')
	result, output = context.TryAction(command)
	context.Result(result)
	return result, output

#@staticmethod
def _try_run(context, packageneric, description, text, language):
	#packageneric.trace('checking for ' + description + ' ... ')
	context.Message('checking for ' + description + ' ... ')
	result, output = context.TryRun(text, language)
	context.Result(result)
	return result, output
	
#@staticmethod
def _dump_environment(environment, all = False):
	if all:
		if False:
			print environment.Dump()
		else:
			dictionary = environment.Dictionary()
			keys = dictionary.keys()
			keys.sort()
			for key in keys:
				print '%s = %s' % (key, dictionary[key])
	else:
		def show(key):
			try:
				environment[key]
				if len(env[key]):
					print key, '->', environment[key], '->', environment.subst('$' + key)
				else:
					print key, '<- empty'
			except:
				pass
		show('CPPDEFINES')
		show('CPPPATH')
		show('CXXFLAGS')
		show('LIBPATH')
		show('LIBS')
		show('LINKFLAGS')

def packageneric(
	ARGUMENTS,
	Environment
):
	class Packageneric:

		def version(
			self,
			major = 0, 
			minor = 0, 
			patch = 0
		):	
			class Version:
				def __init__(
					self, 
					major, 
					minor, 
					patch
				):
					self._major = major
					self._minor = minor
					self._patch = patch

				def major(self):
					return self._major
					
				def minor(self):
					return self._minor
					
				def patch(self):
					return self._patch
					
				def __str__(self):
					return str(self._major) + '.' + str(self._minor) + '.' + str(self._patch)
				
				def __cmp__(self, other):
					result = cmp(self.major(), other.major())
					if result:
						return result
					result = cmp(self.minor(), other.minor())
					if result:
						return result
					return cmp(self.patch(), other.patch())
					
			return Version(
				major,
				minor,
				patch
			)
		
		def environment(self):
			return self._environment
		
		def configure(self):
			return self._configure
		
		def finish_configure(self):
			self._environment = self.configure().Finish()

		def options(self):
			return self._options

		def	self_version(self):
			return self._version
			
		def command_line_arguments(self):
			return self._command_line_arguments
			
		def build_directory(self):
			return self._build_directory
		
		def __init__(
			self,
			ARGUMENTS,
			Environment
		):
			self._version = self.version(0, 0)
			self.information('packageneric version: ' + str(self.self_version()))
			
			self._command_line_arguments = ARGUMENTS
			
			import SCons.Options
			self._options = SCons.Options.Options('packageneric.options', self.command_line_arguments())
			self.options().Add(SCons.Options.PathOption('packageneric__build_directory', 'directory where to build into', os.path.join('++packageneric', 'build', 'scons'), SCons.Options.PathOption.PathIsDirCreate))
			self.options().Add(SCons.Options.PathOption('packageneric__install_stage_destination', 'directory to install under (stage installation)', '.', SCons.Options.PathOption.PathIsDirCreate))
			self.options().Add(SCons.Options.PathOption('packageneric__install_prefix', 'directory to install under (final installation)', os.path.join('usr', 'local'), SCons.Options.PathOption.PathIsDirCreate))
			self.options().Add('packageneric__release', 'set to 1 to build for release', 0)
			
			self._environment = Environment(
				options = self.options(),
				CPPDEFINES = {'PACKAGENERIC__RELEASE' : '$packageneric__release'}
			)
			self.environment().EnsurePythonVersion(2, 3)
			self.environment().EnsureSConsVersion(0, 96)
			
			self.options().Save('packageneric.options', self.environment())
			
			self.environment().Help(self.options().GenerateHelpText(self.environment()))
			self._build_directory = os.path.join(self.environment()['packageneric__build_directory'], 'targets')
			self.environment().BuildDir(self.build_directory(), '.', duplicate = False)
			self.environment().CacheDir(os.path.join(self.environment()['packageneric__build_directory'], 'cache'))

			self._installation_prefix  = '$prefix'
			self._installation_etc     = '/etc'
			self._installation_bin     = '$prefix/bin'
			self._installation_lib     = '$prefix/lib'
			self._installation_include = '$prefix/include'
			self._installation_data    = '$prefix/share'
			self._installation_var     = '$prefix/var'
			if False:
				self.environment().Export('env installation_prefix')
			
			self._configure = self.environment().Configure(
				custom_tests =
				{
					'packageneric__pkg_config' : lambda context, packageneric, name, what: _pkg_config(context, packageneric, name, what),
					'packageneric__try_run' : lambda context, packageneric, description, text, language: _try_run(context, packageneric, description, text, language)
				}
			)

		def person(
			self,
			name,
			email = None
		):
			class Person:
				def __init__(
					self,
					name,
					email
				):
					self._name = name
					self._email = email
					
				def name(self):
					return self._name
				
				def email(self):
					return self._email
					
			return Person(
				name,
				email
			)

		def find(
			self,
			strip_path,
			path, pattern = '*'
		):
			class Find:
				'''a forward iterator that traverses a directory tree'''
				
				def __init__(
					self,
					packageneric,
					strip_path,
					path,
					pattern
				):
					self._packageneric = packageneric
					self._strip_path = strip_path
					self._stack = [path]
					self._pattern = pattern
					self._files = []
					self._index = 0
					
				def packageneric(self):
					return self._packageneric
					
				def strip_path(self):
					return self._strip_path
				
				def __getitem__(self, index):
					while True:
						try:
							file = self._files[self._index]
							self._index += 1
						except IndexError:
							# pop next directory from stack
							self._directory = self._stack.pop()
							self._files = os.listdir(os.path.join(self.strip_path(), self._directory))
							self._index = 0
						else:
							# got a filename
							path = os.path.join(self._directory, file)
							if os.path.isdir(os.path.join(self.strip_path(), path)):
								self._stack.append(path)
							if fnmatch.fnmatchcase(file, self._pattern):
								return path
								
			return Find(
				self,
				strip_path,
				path,
				pattern
			)
		
		def print_all_nodes(dirnode, level = 0):
			'''prints all the scons nodes that are children of this node, recursively.'''
			if type(dirnode)==type(''):
				dirnode=Dir(dirnode)
			dt = type(Dir('.'))
			for f in dirnode.all_children():
				if type(f) == dt:
					print "%s%s: .............." % (level * ' ', str(f))
					print_dir(f, level+2)
				print "%s%s" % (level * ' ', str(f))

		def glob(includes = ['*'], excludes = None, dir = '.'):
			'''similar to glob.glob, except globs SCons nodes, and thus sees generated files and files from build directories.
			Basically, it sees anything SCons knows about.
			A key subtlety is that since this function operates on generated nodes as well as source nodes on the filesystem,
			it needs to be called after builders that generate files you want to include.
			
			It will return both Dir entries and File entries
			'''
			
			def fn_filter(node):
				fn = os.path.basename(str(node))
				match = False
				for include in includes:
					if fnmatch.fnmatchcase(fn, include):
						match = True
						break
				if match and not excludes is None:
					for exclude in excludes:
						if fnmatch.fnmatchcase(fn, exclude):
							match = False
							break
				return match

			def filter_nodes(where):
				children = filter(fn_filter, where.all_children(scan = False))
				nodes = []
				for f in children:
					nodes.append(gen_node(f))
				return nodes

			def gen_node(n):
				'''Checks first to see if the node is a file or a dir, then creates the appropriate node.
				(code seems redundant, if the node is a node, then shouldn't it just be left as is?)
				'''
				if type(n) in (type(''), type(u'')):
					path = n
				else:
					path = n.abspath
				if os.path.isdir(path):
					return Dir(n)
				else:
					return File(n)
			
			here = Dir(dir)
			nodes = filter_nodes(here)
			node_srcs = [n.srcnode() for n in nodes]
			src = here.srcnode()
			if src is not here:
				for s in filter_nodes(src):
					if s not in node_srcs:
						# Probably need to check if this node is a directory
						nodes.append(gen_node(os.path.join(dir, os.path.basename(str(s)))))
			return nodes

		def source_package(
			self,
			name = None,
			version = None,
			description = '',
			long_description = '',
			path = ''
		):
			class SourcePackage:
				def __init__(
					self,
					packageneric,
					name,
					version,
					description,
					long_description,
					path
				):
					self._packageneric = packageneric
					self._name = name
					self._version = version
					self._description= description
					self._long_description = long_description
					self._path = path
				
				def packageneric(self):
					return self._packageneric
				
				def name(self):
					return self._name
					
				def version(self):
					return self._version
					
				def description(self):
					return self._description
					
				def long_description(self):
					return self._long_description
					
				def path(self):
					return self._path
				
			return SourcePackage(
				self,
				name,
				version,
				description,
				long_description,
				path
			)
			
		def tty_font(self, font = '0', text = None):
			result = '\033[' + font + 'm'
			if text:
					result += text + self.tty_font()
			return result
		
		def message(self, message, font = None):
			prefix = __name__ + '(' + self.__class__.__name__ + '): '
			string = prefix
			for x in message:
				string += x
				if x == '\n':
						string += prefix
			if font:
				string = self.tty_font(font, string)
			print string

		def trace(self, message):
			self.message('trace: ' + message, '2;33')
			
		def information(self, message):
			self.message('information: ' + message, '34')
		
		def success(self, message):
			self.message('information: ' + message, '32')
			
		def warning(self, message):
			self.message('warning: ' + message, '35')
		
		def error(self, message):
			self.message('error: ' + message, '1;31')

		def abort(self, message):
			self.error(message + '\nbailing out.')
			sys.exit(1)
		
		def external_package(
				self,
				debian,
				pkg_config = None,
				headers = None,
				libraries = None
		):
			class NameAndLanguage:
				def __init__(self, name, language):
					self._name = name
					self._language = language
				def name(self):
					return self._name
				def language(self):
					return self._language
			
			class Header(NameAndLanguage):
				def __init__(self, name, language):
					NameAndLanguage.__init__(self, name, language)
					
			class Library(NameAndLanguage):
				def __init__(self, name, language):
					NameAndLanguage.__init__(self, name, language)
					
			class ExternalPackage:
				
				def packageneric(self):
					return self._packageneric
				
				def debian(self):
					return self._debian
					
				def pkg_config(self):
					return self._pkg_config
				def _check_pkg_config(self):
					return self.packageneric().configure().packageneric__pkg_config(self.packageneric(), self.pkg_config(), 'exists')

				def headers(self):
					return self._headers
				def add_header(self, name, language = 'C++'):
					self._headers.append(Header(name, language))
				def add_headers(self, name, language = 'C++'):
					for x in names:
						self.add_header(x, language)
				def _check_header(self, header, language = 'C++'):
					return self.packageneric().configure().CheckHeader(header = header, language = language)
					
				def libraries(self):
					return self._libraries
				def add_library(self, name, language = 'C++'):
					self._libraries.append(Library(name, language))
				def add_libraries(self, names, language = 'C++'):
					for x in names:
						self.add_library(x, language)
				def _check_library(self, library, language = 'C++'):
					return self.packageneric().configure().CheckLib(library = library, language = language, autoadd = True)

				def _headers_and_libraries(self, headers, libraries, language = 'C++'):
					return self.packageneric().configure().CheckLibWithHeader(libs = libraries, header = headers, language = language)

				def try_run(self, description, text, language = '.cpp'):
						return_code, output = self.packageneric().configure().packageneric__try_run(self.packageneric(), description, text, language)
						return return_code, output
				
				def __init__(
					self,
					packageneric,
					debian,
					pkg_config,
					headers,
					libraries
				):
					self._packageneric = packageneric
					self._debian = debian
					self._pkg_config = pkg_config
					self._headers = []
					if not headers is None:
						for x in headers:
							if type(x) is type([]):
								self.add_header(x[0], x[1])
							else:
								self.add_header(x)
					self._libraries = []
					if not libraries is None:
						for x in libraries:
							if type(x) is type([]):
								self.add_library(x[0], x[1])
							else:
								self.add_library(x)
					self._found = None
					self._environment = None
					
				def found(self):
					if self._found is None:
						self._found = True
						if not self.pkg_config() is None:
							self._found |= self._check_pkg_config()
						for x in self.headers():
							self._found |= self._check_header(x.name(), x.language())
						for x in self.libraries():
							self._found |= self._check_library(x.name(), x.language())
					return self._found
					
				def environment(self):
					if not self.found():
						packageneric.error('cannot generate environment because dependencies were not found')
					if self._environment is None:
						self._environment = self.packageneric().environment().Copy()
						if not self.pkg_config() is None:
							self._environment.ParseConfig('pkg-config --cflags --libs \'' + self.pkg_config() + '\'')
					return self._environment
					
				def show(self):
					self.packageneric().information('external package: ' + str(self))
					
				def __str__(self):
					string = ''
					if not self.pkg_config() is None:
						string += self.pkg_config()
					else:
						string += self.debian()
					for x in self.headers():
						string += ' ' + x.name()
					for x in self.libraries():
						string += ' ' + x.name()
					return string
				
			return ExternalPackage(
				self,
				debian,
				pkg_config,
				headers,
				libraries
			)
			
		def module(
			self,
			name = None,
			version = None,
			description = '',
			public_requires = None
		):
			class Module:
				class Types:
					files = 'files'
					shared_lib = 'shared_lib'
					static_lib = 'static_lib'
					bin = 'bin'
					python = 'python'
					
				def __init__(
					self, 
					packageneric, 
					name, 
					version, 
					description, 
					public_requires
				):
					self._packageneric = packageneric
					self._name = name
					self._version = version
					self._description = description
					if public_requires is None:
						self._public_requires = []
					else:
						self._public_requires = public_requires
					self._sources = []
					self._headers = []
					self._include_path = []
					self._defines = {}
					self._environment = None
					self._targets = None
				
				def packageneric(self):
					return self._packageneric
					
				def name(self):
					return self._name
				
				def version(self):
					return self._version
				
				def description(self):
					return self._description
					
				def sources(self):
					return self._sources
				def add_source(self, source):
					self.sources().append(os.path.join(self.packageneric().build_directory(), source))
				def add_sources(self, sources):
					for x in sources: self.add_source(x)
					
				def headers(self):
					return self._headers
				def add_header(self, header):
					self.headers().append(header)
				def add_headers(self, headers):
					for x in headers: self.add_header(x)
					
				def include_path(self):
					return self._include_path
				def add_include_path(self, path):
					self._include_path.append(path)
				
				def defines(self):
					return self._defines
				def add_define(self, name, value):
					self._defines.append({name: value})
					
				def public_requires(self):
					return self._public_requires
				def add_public_requires(self, requires):
					self.public_requires().append(requires)
					
				def show(self, list_files = False):
					self.packageneric().information('module: ' + self.name() + ' ' + str(self.version()))
					public_requires = []
					for x in self.public_requires():
						public_requires.append(str(x))
					self.packageneric().information('module: requires: ' + str(public_requires))
					if list_files:
						self.packageneric().trace('module: sources:')
						self.packageneric().trace(str(self.sources()))
						self.packageneric().trace('module: headers:')
						self.packageneric().trace(str(self.headers()))
				
				def environment(self):
					if self._environment is None:
						self._environment = self.packageneric().environment().Copy()
						self._environment.Append(
							CPPPATH = self.include_path(),
							CPPDEFINES = self.defines()
						)
						self._environment.Append(
							CPPDEFINES = {
								'PACKAGENERIC': '\\"/dev/null\\"',
								'PACKAGENERIC__PACKAGE__NAME': '\\"test\\"',
								'PACKAGENERIC__PACKAGE__VERSION': '\\"0\\"',
								'PACKAGENERIC__PACKAGE__VERSION__MAJOR': '0',
								'PACKAGENERIC__PACKAGE__VERSION__MINOR': '0',
								'PACKAGENERIC__PACKAGE__VERSION__PATCH': '0',
								'PACKAGENERIC__MODULE__NAME': '\\"test\\"',
								'PACKAGENERIC__MODULE__VERSION': '\\"0\\"',
								'PACKAGENERIC__CONFIGURATION__INSTALL_PATH__BIN_TO_LIB': '\\"../lib\\"',
								'PACKAGENERIC__CONFIGURATION__INSTALL_PATH__BIN_TO_SHARE': '\\"../share\\"',
								'PACKAGENERIC__CONFIGURATION__INSTALL_PATH__BIN_TO_VAR': '\\"../var\\"',
								'PACKAGENERIC__CONFIGURATION__INSTALL_PATH__BIN_TO_ETC': '\\"../../etc\\"',
								'PACKAGENERIC__CONFIGURATION__COMPILER__HOST': '\\"test\\"'
							}
						)
						pkg_config = ''
						for x in self.public_requires():
							if not x.pkg_config() is None:
								pkg_config += ' ' + x.pkg_config()
						if not pkg_config == '':
							self._environment.ParseConfig('pkg-config --cflags --libs \'' + pkg_config + '\'')
					return self._environment
						
				def targets(self):
					if self._targets is None:
						self._targets = self.environment().SharedLibrary(os.path.join(self.packageneric().build_directory(), self.name()), self.sources())
					return self._targets

			return Module(
				self, 
				name, 
				version, 
				description, 
				public_requires
			)
		
		def pkg_config_package(
			self,
			name = None,
			version = None,
			description = '',
			modules = None
		):
			class PkgConfigPackage:
				def __init__(
					self,
					name,
					version,
					description,
					modules
				):
					self._name = name
					self._version = version
					self._description = description
					if modules is None:
						self._modules = []
					else:
						self._modules = modules
						
				def name(self):
					return self._name
					
				def version(self):
					return self._version
				
				def description(self):
					return self._description
					
				def modules(self):
					return self._modules
			
			return PkgConfigPackage(
				name,
				version,
				description,
				modules
			)

		def debian_package(
			self,
			source_package = None, 
			name = None, 
			section = None, 
			architecture = 'any', 
			description = '', 
			long_description = ''
		):
			class DebianPackage:
				def __init__(
					self,
					source_package,
					name,
					section,
					architecture,
					description,
					long_description
				):
					self._source_package = source_package
					self._name = name
					if section is None:
						self._section = self.source_package().section()
					else:
						self._section = section
					self._architecture = architecture
					self._provides = []
					self._depends = []
					self._recommends = []
					self._suggests = []
					self._description = description
					self._long_description = long_description
					self._files = []
					
				def source_package(self):
					return self._source_package
					
				def name(self):
					return self._name
					
				def section(self):
					return self._section
					
				def architecture(self):
					return self._architecture
				
				def provides(self):
					return self._provides
				
				def	build_depends(self):
					result = []
					for x in self.depends():
						if not x.debian() in result:
							result.append(x.debian())
					return result
				def depends(self): # todo build_depends
					return self._depends
				def add_depend(self, depend):
					self.depends().append(depend)
				def add_depends(self, depends):
					for x in depends:
						self.add_depend(x)
				
				def recommends(self):
					return self._recommends
					
				def suggests(self):
					return self._suggests
				
				def description(self):
					return self._description
					
				def long_description(self):
					return self._long_description

			return DebianPackage(
				source_package,
				name, 
				section, 
				architecture, 
				description, 
				long_description
			)
			
		def debian(
			self, 
			source_package = None, 
			section = 'libs', 
			priority = 'optional',
			maintainer = '',
			uploaders = None,
			description = None,
			long_description = None,
			binary_packages = None,
			build_depends = None
		):
			class Debian:
				def __init__(
					self,
					source_package,
					section,
					priority,
					maintainer,
					uploaders,
					description,
					long_description,
					binary_packages,
					build_depends
				):
					self._source_package = source_package
					self._section = section
					self._priority = priority
					self._maintainer = maintainer
					if uploaders is None:
						self._uploaders = []
					else:
						self._uploaders = uploaders
					if description is None and not source_package is None:
						self._description = source_package.description()
					else:
						self._description = description
					if long_description is None and not source_package is None:
						self._long_description = source_package.long_description()
					else:
						self._description = description
					if binary_packages is None:
						self._binary_packages = []
					else:
						self._binary_packages = binary_packages
					if build_depends is None:
						self._build_depends = []
					else:
						self._build_depends = build_depends

				def source_package(self):
					return self._source_package
					
				def section(self):
					return self._section
					
				def priority(self):
					return self._priority
					
				def maintainer(self):
					return self._maintainer
					
				def uploaders(self):
					return self._uploaders
					
				def description(self):
					return self._description
					
				def long_description(self):
					return self._long_description
					
				def binary_packages(self):
					return self._binary_packages
					
				def	build_depends(self):
					result = self._build_depends
					for x in self.binary_packages():
						for xx in x.build_depends():
							if not xx in self._build_depends:
								result.append(xx)
					return result
				
				def control(self):
					string = ''
					string += 'Source: ' + self.source_package().name() + '\n'
					string += 'Section: ' + self.section() + '\n'
					string += 'Priority: ' + self.priority() + '\n'
					string += 'Build-Depends: scons'
					for x in self.build_depends():
						string += ', ' + x
					string += '\n'
					if not self.maintainer() is None:
						string += 'Maintainer: ' + self.maintainer().name() + ' <' + self.maintainer().email() + '>\n'
					if len(self.uploaders()):
						string += 'Uploaders: '
						for x in self.uploaders():
							string += x.name() + ' <' + x.email() + '>, '
						string += '\n'
					string += 'Standards-Version: 3.6.2\n'
					for x in self.binary_packages():
						string += '\n'
						string += 'Package: ' + x.name() + '\n'
						if len(x.provides()):
							string += 'Provides: '
							for xx in x.provides():
								string += xx + ', '
							string += '\n'
						if len(x.recommends()):
							string += 'Recommends: '
							for xx in x.recommends():
								string += xx.name() + ' (' + xx.version_compare(), '), '
							string += '\n'
						if len(x.suggests()):
							string += 'Suggests: '
							for xx in x.suggests():
								string += xx.name() + ' (' + xx.version_compare() + '), '
							string += '\n'
						string += 'Depends: ${shlibs:Depends}, ${misc:Depends}'
						#for xx in x.depends():
						#	string += ', ' + x
						string += '\n'
						string += 'Section: '
						if x.section() is None:
							string += self.section()
						else:
							string += x.section()
						string += '\n'
						string += 'Architecture: ' + x.architecture() + '\n'
						string += 'Description: ' + x.description() + '\n '
						description = self.long_description() + '\n\n' + x.long_description()
						was_new_line = False
						for xx in description:
							if xx == '\n':
								if was_new_line:
									string += '.'
								was_new_line = True
								string += '\n '
							else:
								was_new_line = False
								string += xx
						string += '\n'
					return string
					
			return Debian(
				source_package,
				section,
				priority,
				maintainer,
				uploaders,
				description,
				long_description,
				binary_packages,
				build_depends
			)


		def distribution_archive(
			self,
			remote_path = None,
			source_packages = [],
			binary_packages = []
		):
			class DistributionArchive:
				def __init__(
					self,
					remote_path,
					source_packages,
					binary_packages
				):
					self._remote_path = remote_path
					self._source_packages = source_packages
					self._binary_packages = binart_packages
					
				def remote_path(self):
					return self._remote_path
					
				def source_packages(self):
					return self._source_packages
					
				def binary_packages(self):
					return self._binary_packages

			return DistributionArchive(
				self,
				remote_path,
				source_packages,
				binary_packages
			)
			
	return Packageneric(
		ARGUMENTS,
		Environment
	)
