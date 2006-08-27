#! /usr/bin/env python

# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006 johan boule <bohan@jabber.org>
# copyright 2006 psycledelics http://psycle.pastnotecut.org

import sys, os.path

class packageneric:

	from person import person
	from version import version
	
	def source_package(self, *args, **kw):
		from source_package import source_package
		return apply(source_package, (self,) + args, kw)
		
	def find(self, *args, **kw):
		from find import find
		return apply(find, (self,) + args, kw)

	from find import glob, print_all_nodes
	
	def external_package(self, *args, **kw):
		from external_package import external_package
		return apply(external_package, (self,) + args, kw)
		
	def module(self, *args, **kw):
		from module import module
		return apply(module, (self,) + args, kw)
		
	def pkg_config_package(self, *args, **kw):
		from pkg_config_package import pkg_config_package
		return apply(pkg_config_package, (self,) + args, kw)
		
	def debian_package(self, *args, **kw):
		from debian_package import debian_package
		return apply(debian_package, (self,) + args, kw)
		
	def debian(self, *args, **kw):
		from debian import debian
		return apply(debian, (self,) + args, kw)
		
	def distribution_archive(self, *args, **kw):
		from distribution_archive import distribution_archive
		return apply(distribution_archive, (self,) + args, kw)
		
	def environment(self):
		return self._environment
	
	def configure(self):
		if self._configure is None:
			self.trace('creating configure')
			self._configure = self.environment().Configure(
				custom_tests =
				{
					'packageneric__pkg_config' : lambda context, packageneric, name, what: _pkg_config(context, packageneric, name, what),
					'packageneric__try_run' : lambda context, packageneric, description, text, language: _try_run(context, packageneric, description, text, language),
					'packageneric__free' : lambda context, packageneric, free: _free(context, packageneric, free)
				},
				conf_dir = os.path.join(self.environment()['packageneric__build_directory'], 'configure'),
				log_file = os.path.join(self.environment()['packageneric__build_directory'], 'configure.log'),
				config_h = os.path.join(self.environment()['packageneric__build_directory'], 'configure.hpp')
			)
			self._configure_finished = False
		return self._configure
	
	def finish_configure(self):
		if not self._configure_finished:
			self._configure_finished = True
			self.trace('configure finished')
			self._environment = self.configure().Finish()
			self._configure = None
			#_dump_environment(self.environment())

	def options(self):
		return self._options

	def	self_version(self):
		return self._version
		
	def command_line_arguments(self):
		return self._command_line_arguments
		
	def build_directory(self):
		return self._build_directory
	
	def __init__(self):
		self._version = self.version(0, 0)
		self.information('packageneric version: ' + str(self.self_version()))
		
		import SCons.Script.SConscript
		self._command_line_arguments = SCons.Script.SConscript.Arguments
		
		import SCons.Options
		self._options = SCons.Options.Options('packageneric.options', self.command_line_arguments()) # todo cache in packageneric__build_directory
		self.options().Add(SCons.Options.PathOption('packageneric__build_directory', 'directory where to build into', os.path.join('packageneric', '++build'), SCons.Options.PathOption.PathIsDirCreate))
		self.options().Add(SCons.Options.PathOption('packageneric__install_stage_destination', 'directory to install under (stage installation)', os.path.join('packageneric', '++install-stage'), SCons.Options.PathOption.PathIsDirCreate))
		self.options().Add(SCons.Options.PathOption('packageneric__install_prefix', 'directory to install under (final installation)', os.path.join('packageneric', '++install'), SCons.Options.PathOption.PathIsDirCreate))
		#self.options().Add('CXX', 'the c++ compiler')
		#self.options().Add('LD', 'the linker')
		self.options().Add('packageneric__release', 'set to 1 to build for release', 0)
		
		from SCons.Script.SConscript import SConsEnvironment as environment
		self._environment = environment(
			options = self.options(),
			toolpath = ['packageneric/generic/tools'],
			tools = ['default', 'subst']
		)

		self.environment().EnsurePythonVersion(2, 3)
		self.environment().EnsureSConsVersion(0, 96)
		self.environment().SetOption('implicit_cache', True)
		#self.environment().SourceSignatures('timestamp') # ('MD5')
		self.environment().TargetSignatures('build') # ('content')

		self.options().Save('packageneric.options', self.environment()) # todo cache in packageneric__build_directory
		
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
			
		if False:
			self.environment().Append(
				CPPDEFINES = {
					'PACKAGENERIC__RELEASE' : '$packageneric__release',
					'PACKAGENERIC__CONFIGURATION__INSTALL_PATH__BIN_TO_LIB': '\\"../lib\\"',
					'PACKAGENERIC__CONFIGURATION__INSTALL_PATH__BIN_TO_SHARE': '\\"../share\\"',
					'PACKAGENERIC__CONFIGURATION__INSTALL_PATH__BIN_TO_VAR': '\\"../var\\"',
					'PACKAGENERIC__CONFIGURATION__INSTALL_PATH__BIN_TO_ETC': '\\"../../etc\\"',
					'PACKAGENERIC__CONFIGURATION__COMPILER__HOST': '\\"test\\"'
				}
			)
		
		self.environment().Append(
			SUBST_DICT = {
				'#undef PACKAGENERIC__RELEASE' : '#define $packageneric__release',
				'#undef PACKAGENERIC__CONFIGURATION__INSTALL_PATH__BIN_TO_LIB': '#define PACKAGENERIC__CONFIGURATION__INSTALL_PATH__BIN_TO_LIB "../lib"',
				'#undef PACKAGENERIC__CONFIGURATION__INSTALL_PATH__BIN_TO_SHARE': '#define PACKAGENERIC__CONFIGURATION__INSTALL_PATH__BIN_TO_SHARE "../share"',
				'#undef PACKAGENERIC__CONFIGURATION__INSTALL_PATH__BIN_TO_VAR': '#define PACKAGENERIC__CONFIGURATION__INSTALL_PATH__BIN_TO_VAR "../var"',
				'#undef PACKAGENERIC__CONFIGURATION__INSTALL_PATH__BIN_TO_ETC': '#define PACKAGENERIC__CONFIGURATION__INSTALL_PATH__BIN_TO_ETC "../../etc"',
				'#undef PACKAGENERIC__CONFIGURATION__COMPILER__HOST': '#define PACKAGENERIC__CONFIGURATION__COMPILER__HOST "test"'
			}
		)
		for i in self.find('.', '.', '*.hpp.in'):
			self.environment().SubstInFile(
				os.path.join(self.build_directory(), os.path.splitext(i)[0]),
				i
			)
			self.environment().SubstInFile(
				os.path.join(self.build_directory(), os.path.splitext(os.path.splitext(i)[0])[0] + '.private.hpp'),
				i
			)
		self.environment().Append(
			CPPPATH = self.build_directory()
		)
		
		self._configure = None
		
		self._indentation = 0
		self._indentation_pushed = True

	def indentation(self):
		result = ''
		if self._indentation_pushed:
			self._indentation_pushed = False
			result += '\n'
		return result + ' -> ' * self._indentation
		
	def push_indentation(self):
		self._indentation += 1
		self._indentation_pushed = True
		
	def pop_indentation(self):
		self._indentation -= 1
		self._indentation_pushed = False

	def tty_font(self, font = '0', text = None):
		result = '\033[' + font + 'm'
		if text:
				result += text + self.tty_font()
		return result
	
	def message(self, message, font = None):
		#prefix = __name__ + '(' + self.__class__.__name__ + '): '
		prefix = 'packageneric: '
		string = prefix
		for x in message:
			string += x
			if x == '\n':
					string += prefix
		if font:
			string = self.tty_font(font, string)
		return string

	def trace(self, message):
		print self.message('trace: ' + message, '2;33')
		
	def information(self, message):
		print self.message('information: ' + message, '34')
	
	def success(self, message):
		print self.message('information: ' + message, '32')
		
	def warning(self, message):
		print self.message('warning: ' + message, '35')
	
	def error(self, message):
		print self.message('error: ' + message, '1;31')

	def abort(self, message):
		self.error(message + '\nbailing out.')
		sys.exit(1)

#@staticmethod
def _pkg_config(context, packageneric, name, what):
	command = 'pkg-config --%s \'%s\'' % (what, name)
	#packageneric.trace('checking for ' + command + ' ... ')
	context.Display(packageneric.indentation())
	context.Message(packageneric.message('checking for ' + command + ' ... '))
	result, output = context.TryAction(command)
	context.Result(result)
	return result, output

#@staticmethod
def _try_run(context, packageneric, description, text, language):
	#packageneric.trace('checking for ' + description + ' ... ')
	context.Display(packageneric.indentation())
	context.Message(packageneric.message('trying to build and run program for checking ' + description + ' ... '))
	result, output = context.TryRun(text, language)
	context.Result(result)
	return result, output
	
#@staticmethod
def _free(context, packageneric, free):
	#packageneric.trace('checking for ' + str(free) + ' ... ')
	context.Display(packageneric.indentation())
	context.Display(packageneric.message('checking for ' + str(free) + ' ... '))
	packageneric.push_indentation()
	result = free()
	context.Display(packageneric.indentation())
	context.Display(packageneric.message('checking for ' + str(free) + ' ... '))
	packageneric.pop_indentation()
	context.Result(result)
	return result

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
				if len(environment[key]):
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
