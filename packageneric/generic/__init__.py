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

	def name(self): return self._name
			
	def	self_version(self):
		if not self._version:
			self._version = self.version(0, 0)
		return self._version

	def targets(self): return self._targets
	def add_target(self, builder): self._targets[builder.target_name()] = builder

	def __call__(self, *builders):
		import SCons.Script, SCons.Node.Alias
		#SCons.Script.main()
		self.information('targets: ' + ' '.join(SCons.Script.BUILD_TARGETS) + ' '.join(map(lambda x: x.target_name(), builders)))
		for builder in builders:
			self.common_environment().Alias(builder.target_name(), builder.targets())
			self.common_environment().Default(builder.target_name())
		for (target, builder) in self.targets().items():
			if target in SCons.Script.BUILD_TARGETS: self.common_environment().Alias(target, builder.targets())
	
	def command_line_arguments(self):
		if self._command_line_arguments is None:
			import SCons.Script
			self._command_line_arguments = SCons.Script.ARGUMENTS
		return self._command_line_arguments
		
	def options(self):
		if not self._options:
			# We create the SCons.Options.Options object in two steps because we first want to know
			# whether an option file was specified on the command line or env via the option packageneric__options
			# and then we create again the SCons.Options.Options object telling it to read the option file.
			def restart(self, create_build_directory):
				# Options which impact on the path of the option file are put here,
				# that is, the option packageneric__options itself,
				# and the other options that its default value is defined as, recursively.
				self._options.Add('packageneric__build_variant', 'subdirectory where to build into', 'default')
				if create_build_directory: self._options.Add(SCons.Options.PathOption('packageneric__build_directory', 'directory where to build into', os.path.join('packageneric', '++build', '$packageneric__build_variant'), SCons.Options.PathOption.PathIsDirCreate))
				else: self._options.Add('packageneric__build_directory', 'directory where to build into', os.path.join('packageneric', '++build', '$packageneric__build_variant'))
				self._options.Add('packageneric__options', 'file where to read options from', os.path.join('$packageneric__build_directory', 'options'))
			import SCons.Options
			# We don't know yet the path of the option file,
			# so we pass None as the filename.
			self._options = SCons.Options.Options(None, self.command_line_arguments())
			restart(self, create_build_directory = False)
			self._options.Update(self.common_environment())
			# Now that we know the path of the option file,
			# we create again the SCons.Options.Options object telling it to read the option file.
			self.information('using options ' + self.common_environment().subst('$packageneric__options'))
			self._options = SCons.Options.Options(self.common_environment().subst('$packageneric__options'), self.command_line_arguments())
			restart(self, create_build_directory = True)
			self._options.Add(SCons.Options.PathOption('packageneric__install__stage_destination', 'directory to install under (stage installation)', os.path.join('$packageneric__build_directory', 'stage-install'), SCons.Options.PathOption.PathIsDirCreate))
			self._options.AddOptions(
				('packageneric__install__prefix', 'directory to install under (final installation)', os.path.join('/', 'opt', self.name())),
				('packageneric__install__exec_prefix', 'directory to install architecture-dependant excecutables under (final installation)', '$packageneric__install__prefix'),
				('packageneric__install__bin', 'directory to install programs under (final installation)', os.path.join('$packageneric__install__exec_prefix', 'bin')),
				('packageneric__install__lib', 'directory to install libraries under (final installation)', os.path.join('$packageneric__install__exec_prefix', 'lib')),
				('packageneric__install__lib_exec', 'directory to install helper programs under (final installation)', os.path.join('$packageneric__install__exec_prefix', 'libexec')),
				('packageneric__install__include', 'directory to install headers under (final installation)', os.path.join('$packageneric__install__prefix', 'include')),
				('packageneric__install__share', 'directory to install archictecture-independent data under (final installation)', os.path.join('$packageneric__install__prefix', 'share')),
				('packageneric__install__var', 'directory to install machine-specific state-variable data under (final installation)', os.path.join('$packageneric__install__prefix', 'var')),
				('packageneric__install__etc', 'directory to install machine-specific configuration files under (final installation)', os.path.join('/', 'etc')),
				('packageneric__cxx_compiler', 'the c++ compiler (default value was autodetected)', self.common_environment().subst('$SHCXX')),
				('packageneric__linker', 'the linker (default value was autodetected)', self.common_environment().subst('$SHLINK')),
				('packageneric__verbose', 'set to 1 for build verbiage', '0'),
				('packageneric__debug', 'set to 1 to build for debugging', '0'),
				('packageneric__test', 'set to 1 to perform unit tests', '1')
			)
			self._options.Update(self.common_environment())
			self._options.Save(self.common_environment().subst('$packageneric__options'), self.common_environment())
			self._options.format = '\n%s: %s\n    default: %s\n     actual: %s\n'
		return self._options
		
	def build_directory(self):
		if not self._build_directory: self._build_directory = os.path.join('$packageneric__build_directory', 'targets')
		return self._build_directory
	
	def common_environment(self):
		if not self._common_environment:
			import SCons.Environment
			self._common_environment = SCons.Environment.Environment()
			import SCons.Tool
			toolpath = [os.path.join('packageneric', 'generic', 'tools')]
			SCons.Tool.Tool('subst', toolpath = toolpath)(self._common_environment)
			SCons.Tool.Tool('write', toolpath = toolpath)(self._common_environment)
			self._common_environment.SetOption('implicit_cache', True)
			#self._common_environment.SourceSignatures('timestamp') # ('MD5')
			self._common_environment.TargetSignatures('build') # ('content')
			self._common_environment.Help(self.options().GenerateHelpText(self._common_environment))
			# Below are settings which depend on self.options(), that we just called above
			self._common_environment.BuildDir(self.build_directory(), '.', duplicate = False)
			self._common_environment.CacheDir(os.path.join('$packageneric__build_directory', 'cache'))
			self._common_environment.SConsignFile(os.path.join('$packageneric__build_directory', 'signatures'))
		return self._common_environment
		
	def build_environment(self):
		if not self._build_environment:
			self._build_environment = self.common_environment().Copy()
			self._build_environment['SHCXX'] = '$packageneric__cxx_compiler'
			self._build_environment['SHLINK'] = '$packageneric__linker'
			if self._build_environment.subst('$packageneric__verbose') == '0':
				self._build_environment['SHCXXCOMSTR'] = self.message('packageneric: ', 'compiling c++ $TARGET')
				self._build_environment['SHLINKCOMSTR'] = self.message('packageneric: ', 'linking shared library $TARGET')
			self._build_environment.Append(CPPPATH = [os.path.join(self.build_directory(), 'packageneric', 'src')])
			import SCons.Node.Python
			self._build_environment.WriteToFile(
				os.path.join(self.build_directory(), 'packageneric', 'src', 'packageneric', 'configuration.private.hpp'),
				SCons.Node.Python.Value(''.join(['#define PACKAGENERIC__CONFIGURATION__%s %s\n' % (n, v) for n, v in
					[('INSTALL_PATH__BIN_TO_%s' % n, '"%s"' % v) for n, v in
						('LIB', '../lib'),
						('SHARE', '../share'),
						('VAR', '../var'),
						('ETC', '../../etc')
					] +
					[('COMPILER__HOST', '"%s"' % self._build_environment.subst('$packageneric__cxx_compiler'))]
				]))
			)
			for i in self.find('.', '.', '*.hpp.in'): # todo private and public
				self.uninstalled_environment().SubstInFile(os.path.join(self.build_directory(), i.strip(), os.path.splitext(i.relative())[0]), i.full())
				self.build_environment().SubstInFile(os.path.join(self.build_directory(), i.strip(), os.path.splitext(os.path.splitext(i.relative())[0])[0] + '.private.hpp'), i.full())
		return self._build_environment
	
	def uninstalled_environment(self):
		if not self._uninstalled_environment:
			self._uninstalled_environment = self.common_environment().Copy()
			self._uninstalled_environment.Append(
				LIBPATH = [self.build_directory()]
			)	
		return self._uninstalled_environment
		
	def installed_environment(self):
		if not self._installed_environment:
			self._installed_environment = self.common_environment().Copy()
			self._installed_environment.Append(
				CPPPATH = ['$packageneric__install__include'],
				LIBPATH = ['$packageneric__install__lib']
			)	
		return self._installed_environment
		
	def __init__(self, name):
		import SCons.Script
		SCons.Script.EnsureSConsVersion(0, 96)
		SCons.Script.EnsurePythonVersion(2, 3)
		SCons.Script.Default()
		
		self._name = name
		self._version = None
		self._command_line_arguments = None
		self._options = None
		self._build_directory = None
		self._common_environment = None
		self._build_environment = None
		self._uninstalled_environment = None
		self._installed_environment = None
		self._targets = {}
		self._indentation = 0
		
		self.information('version of packageneric: ' + str(self.self_version()))
		
		if False:
			packageneric = self
			self.common_environment().Export('packageneric')
		
	def indentation(self):
		return ' -> ' * self._indentation
		
	def push_indentation(self):
		self._indentation += 1
		
	def pop_indentation(self):
		self._indentation -= 1

	def message(self, prefix, message, font = None):
		#prefix_ = __name__ + '(' + self.__class__.__name__ + '): '
		prefix_ = ''
		if font: prefix_ += tty_font(font)
		prefix_ += prefix
		prefix_ += self.indentation()
		result = prefix_
		for x in message[:-1]:
			if x == '\n':
				if font: result += tty_font()
				result += '\n'
				result += prefix_
			else: result += x
		if len(message): result += message[-1]
		result += tty_font()
		return result

	def trace(self, message): print self.message('packageneric: trace: ', message, '2;33')
		
	def information(self, message): print self.message('packageneric: information: ', message, '34')
	
	def success(self, message): print self.message('packageneric: success: ', message, '32')
		
	def warning(self, message): print self.message('packageneric: warning: ', message, '35')
	
	def error(self, message): print self.message('packageneric: error: ', message, '1;31')

	def abort(self, message):
		self.error(message + '\nbailing out.')
		sys.exit(1)

#@staticmethod
def tty_font(font = '0', text = None):
	if not sys.stdout.isatty():
		if text: return text
		else: return ''
	result = '\033[' + font + 'm'
	if text: result += text + tty_font()
	return result
	
#@staticmethod
def _merge_environment(source, destination):
	try: destination.AppendUnique(CPPFLAGS = source['CPPFLAGS'])
	except KeyError: pass
	try: destination.Append(CPPDEFINES = source['CPPDEFINES'])
	except KeyError: pass
	try: destination.AppendUnique(CPPPATH = source['CPPPATH'])
	except KeyError: pass
	try: destination.AppendUnique(CXXFLAGS = source['CXXFLAGS'])
	except KeyError: pass
	try: destination.AppendUnique(LINKFLAGS = source['LINKFLAGS'])
	except KeyError: pass
	try: destination.AppendUnique(LIBPATH = source['LIBPATH'])
	except KeyError: pass
	try: destination.AppendUnique(LIBS = source['LIBS'])
	except KeyError: pass
	
#@staticmethod
def _dump_environment(environment, all = False):
	if all:
		if False: print environment.Dump()
		else:
			dictionary = environment.Dictionary()
			keys = dictionary.keys()
			keys.sort()
			for key in keys: print '%s = %s' % (key, dictionary[key])
	else:
		def show(key):
			try:
				environment[key]
				if len(environment[key]): print key, '->', environment[key], '->', environment.subst('$' + key)
				else: print key, '<- empty'
			except KeyError: pass
		for x in 'CPPFLAGS', 'CPPDEFINES', 'CPPPATH', 'CXXFLAGS', 'LIBPATH', 'LIBS', 'LINKFLAGS': show(x)
