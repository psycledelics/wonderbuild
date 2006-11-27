# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006 johan boule <bohan@jabber.org>
# copyright 2006 psycledelics http://psycle.pastnotecut.org

import sys, os.path
from tty_font import tty_font

class project:

	def __init__(self, name):
		import SCons.Script
		SCons.Script.EnsureSConsVersion(0, 96, 90) # todo doesn't work with all scons versions
		SCons.Script.EnsurePythonVersion(2, 3) # todo doesn't work with all scons versions
		SCons.Script.Default() # todo doesn't work with all scons versions
		self._name = name
		self.information('project name is ' + self.name())
		self.information('version of packageneric is ' + str(self.self_version()))
		self._scons() # SConscriptChDir(0) src_dir build_dir

	def name(self): return self._name
			
	def	self_version(self):
		try: return self._version
		except AttributeError:
			from version import version
			self._version = version(0, 0)
			return self._version

	def builders(self):
		try: return self._builders
		except AttributeError:
			self._builders = []
			return self._builders
	def add_builder(self, builder):
		self.builders().append(builder)
		self.trace('added builder ' + builder.name() + ' ' + ' '.join(builder.alias_names()))

	def __call__(self, *builders):
		import SCons.Script
		targets = []
		for target in [str(maybe_node) for maybe_node in SCons.Script.BUILD_TARGETS]: targets.append(target)
		for target in [builder.name() for builder in builders]: targets.append(target)
		self.information('targets are ' + ' '.join(targets))
		for builder in builders:
			scons = self._scons()
			scons.Alias(builder.alias_names(), builder.targets())
			scons.Default(builder.alias_names()[0])
		for target in SCons.Script.COMMAND_LINE_TARGETS:
			for builder in self.builders():
				for alias in builder.alias_names():
					if target == alias: scons.Alias(target, builder.targets())
	
	def command_line_arguments(self):
		try: return self._command_line_arguments
		except AttributeError:
			import SCons.Script
			self._command_line_arguments = SCons.Script.ARGUMENTS # todo doesn't work with all scons versions
			return self._command_line_arguments
		
	def packageneric_directory(self):
		import packageneric
		return packageneric.__path__[0]
	
	def build_directory(self):
		try: return self._build_directory
		except AttributeError:
			self._build_directory = self._scons().Dir(os.path.join('$packageneric__build_directory', 'targets', '$packageneric__build_variant', self.name())).path
			return self._build_directory

	def env_class(self):
		try: return self._env_class
		except AttributeError:
			from env import env
			import os_env
			import cxx
			self._env_class = \
				cxx.template(
				os_env.template(
				env))
			return self._env_class
		
	def contexes(self):
		try: return self._contexes
		except AttributeError:
			self.trace('creating build env')
			import contexes
			self._contexes = contexes.template(self.env_class())(self)
			chain = self._contexes.build()
			chain.compilers().cxx().command().set('$packageneric__cxx_compiler')
			chain.linker().command().set('$packageneric__linker') # todo SMARTLINK for C++ vs C
			scons = self._scons()
			self.information('c++ compiler is ' + scons.subst('$CXX') + ' version ' + scons.subst('$CXXVERSION'))
			if scons.subst('$packageneric__verbose') == '0':
				if scons['STATIC_AND_SHARED_OBJECTS_ARE_THE_SAME']:
					chain.compilers().cxx().static().message().set(self.message('packageneric: ', 'compiling object from c++ $SOURCE', font = '1'))
					chain.compilers().cxx().shared().message().set(self.message('packageneric: ', 'compiling object from c++ $SOURCE', font = '1'))
				else:
					chain.compilers().cxx().static().message().set(self.message('packageneric: ', 'compiling static object from c++ $SOURCE', font = '1'))
					chain.compilers().cxx().shared().message().set(self.message('packageneric: ', 'compiling shared object from c++ $SOURCE', font = '1'))
				chain.archiver().message().set(self.message('packageneric: ', 'archiving objects into $TARGET', font = '1;35'))
				chain.archiver().indexer().message().set(self.message('packageneric: ', 'building symbol index table in archive $TARGET', font = '1;35'))
				chain.linker().static().message().set(self.message('packageneric: ', 'linking program $TARGET', font = '1;35'))
				chain.linker().shared().message().set(self.message('packageneric: ', 'linking shared library $TARGET', font = '1;35'))
				chain.linker().loadable().message().set(self.message('packageneric: ', 'linking loadable module $TARGET', font = '1;35'))
			if scons.subst('$packageneric__debug') == '0': debug = False
			else: debug = True
			from gnu import gnu
			gnu(chain, debug)
			chain.compilers().cxx().paths().add([os.path.join(self.build_directory(), 'packageneric', 'src')])
			scons.FileFromValue(
				os.path.join(self.build_directory(), 'packageneric', 'src', 'packageneric', 'configuration.private.hpp'),
				''.join(['#define PACKAGENERIC__CONFIGURATION__%s %s\n' % (n, v) for n, v in
					[('INSTALL_PATH__BIN_TO_%s' % n, '"%s"' % v) for n, v in
						('LIB', '../lib'),
						('SHARE', '../share'),
						('VAR', '../var'),
						('ETC', '../../etc')
					] +
					[('COMPILER__HOST', '"' + scons.subst('$CXX') + ' version ' + scons.subst('$CXXVERSION') + '"')]
				])
			)
			from find import find
			for i in find(self, '.', '.', '*.hpp.in'): # todo private and public
				self.trace(i.relative())
				scons.SubstitutedFile(
					os.path.join(self.build_directory(), i.strip(), os.path.splitext(i.relative())[0]),
					i.full()
				)
				scons.SubstitutedFile(
					os.path.join(self.build_directory(), i.strip(), os.path.splitext(os.path.splitext(i.relative())[0])[0] + '.private.hpp'),
					i.full()
				)
			self._contexes.client().uninstalled().linker().paths().add([self.build_directory()])
			self._contexes.client().installed().compilers().cxx().paths().add(['$packageneric__install__include'])
			self._contexes.client().installed().linker().paths().add(['$packageneric__install__lib'])
			return self._contexes
			
	def _scons(self):
		try: return self._scons_
		except AttributeError:
			import SCons.Environment
			scons = self._scons_ = SCons.Environment.Environment()
			if False:
				try: scons.Import('packageneric')
				except: pass
				else: pass #scons = self._scons_ = ...
			import SCons.Tool
			toolpath = [os.path.join(self.packageneric_directory(), 'generic', 'scons', 'tools')]
			SCons.Tool.Tool('file_from_value', toolpath = toolpath)(scons)
			SCons.Tool.Tool('substituted_file', toolpath = toolpath)(scons)
			scons.SourceCode('.', None) # we don't use the default source code fetchers (RCS, SCCS, ...), so we disable them to avoid uneeded processing
			scons.SetOption('implicit_cache', True)
			#scons.SourceSignatures('timestamp') # scons 0.96.92.0002 bugs with timestamps of symlinks, or even, always ignores all changes!
			scons.SourceSignatures('MD5')
			scons.TargetSignatures('build')
			#scons.TargetSignatures('content')
			self._options()
			# Below are settings which depend on self._options(), that we just called above
			try: self.__class__._scons_called
			except AttributeError:
				self.__class__._scons_called = scons
				scons.Help(self._options().GenerateHelpText(scons))
				# Below are settings which depend on self.options(), that we just called above
				cache = os.path.join('$packageneric__build_directory', 'cache')
				self.information('cache directory is ' + scons.Dir(cache).path)
				scons.CacheDir(cache)
				signature = os.path.join('$packageneric__build_directory', 'signatures')
				self.information('signature  file is ' + scons.Dir(signature).path)
				scons.SConsignFile(signature)
			scons.BuildDir(self.build_directory(), '.', duplicate = False)
			scons.Export({'packageneric': self})
			if False:
				def echo(string, target, source, env): print 'building ' + ' '.join(map(str, target))
				scons['PRINT_CMD_LINE_FUNC'] = echo
			return self._scons_

	def _options(self):
		try: return self._options_
		except AttributeError:
			# We create the SCons.Options.Options object in two steps because we first want to know
			# whether an option file was specified on the command line or env via the option packageneric__options
			# and then we create again the SCons.Options.Options object telling it to read the option file.
			def restart(self, create_build_directory):
				# Options which impact on the path of the option file are put here,
				# that is, the option packageneric__options itself,
				# and the other options that its default value is defined as, recursively (currently there are none).
				if create_build_directory: self._options_.Add(SCons.Options.PathOption('packageneric__build_directory', 'directory where to build into', os.path.join('packageneric', '++build'), SCons.Options.PathOption.PathIsDirCreate))
				else: self._options_.Add('packageneric__build_directory', 'directory where to build into', os.path.join('packageneric', '++build'))
				self._options_.Add('packageneric__options', 'file where to read options from', os.path.join('$packageneric__build_directory', 'options'))
			import SCons.Options
			# We don't know yet the path of the option file,
			# so we pass None as the filename.
			# todo we can actually read the packageneric__build_directory and packageneric__options on command line arguments directly, without creating an option object.
			self._options_ = SCons.Options.Options(None, self.command_line_arguments())
			restart(self, create_build_directory = False)
			scons = self._scons()
			self._options_.Update(scons)
			# Now that we know the path of the option file,
			# we create again the SCons.Options.Options object telling it to read the option file.
			self.information('source directory is ' + scons.Dir('.').path)
			self.information('build  directory is ' + scons.Dir('$packageneric__build_directory').path)
			self.information('options file is ' + scons.subst('$packageneric__options'))
			self._options_ = SCons.Options.Options(scons.subst('$packageneric__options'), self.command_line_arguments())
			restart(self, create_build_directory = True)
			self._options_.Add(SCons.Options.PathOption('packageneric__install__stage_destination', 'directory to install under (stage installation)', os.path.join('$packageneric__build_directory', 'stage-install'), SCons.Options.PathOption.PathIsDirCreate))
			self._options_.AddOptions(
				('packageneric__build_variant', 'subdirectory where to build into', 'default'),
				('packageneric__install__prefix', 'directory to install under (final installation)', os.path.join('/', 'opt', self.name())),
				('packageneric__install__exec_prefix', 'directory to install architecture-dependant excecutables under (final installation)', '$packageneric__install__prefix'),
				('packageneric__install__bin', 'directory to install programs under (final installation)', os.path.join('$packageneric__install__exec_prefix', 'bin')),
				('packageneric__install__lib', 'directory to install libraries under (final installation)', os.path.join('$packageneric__install__exec_prefix', 'lib')),
				('packageneric__install__lib_exec', 'directory to install helper programs under (final installation)', os.path.join('$packageneric__install__exec_prefix', 'libexec')),
				('packageneric__install__include', 'directory to install headers under (final installation)', os.path.join('$packageneric__install__prefix', 'include')),
				('packageneric__install__share', 'directory to install archictecture-independent data under (final installation)', os.path.join('$packageneric__install__prefix', 'share')),
				('packageneric__install__var', 'directory to install machine-specific state-variable data under (final installation)', os.path.join('$packageneric__install__prefix', 'var')),
				('packageneric__install__etc', 'directory to install machine-specific configuration files under (final installation)', os.path.join('/', 'etc')),
				('packageneric__cxx_compiler', 'the c++ compiler (default value was autodetected)', scons.subst('$SHCXX')),
				('packageneric__linker', 'the linker (default value was autodetected)', scons.subst('$SHLINK')),
				('packageneric__verbose', 'set to 1 for build verbiage', '0'),
				('packageneric__debug', 'set to 1 to build for debugging', '0'),
				('packageneric__test', 'set to 1 to perform unit tests', '1')
			)
			self._options_.Update(scons)
			self.information('build variant is ' + scons.subst('$packageneric__build_variant'))
			self._options_.Save(scons.subst('$packageneric__options'), scons)
			self._options_.format = '\n%s: %s\n    default: %s\n     actual: %s\n'
			return self._options_
		
	def message(self, prefix, message, font = None):
		prefix_ = ''
		if font: prefix_ += tty_font(font)
		prefix_ += prefix
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

	def trace(self, message): print self.message('packageneric: trace: ', message, font = '2;33')
		
	def information(self, message): print self.message('packageneric: information: ', message, font = '2;34')
	
	def success(self, message): print self.message('packageneric: success: ', message, font = '32')
		
	def warning(self, message): print self.message('packageneric: warning: ', message, font = '1;35')
	
	def error(self, message): print self.message('packageneric: error: ', message, font = '1;31')

	def abort(self, message):
		print self.message('packageneric: error: ', message, font = '31')
		self.error('bailing out.')
		import SCons.Errors
		raise SCons.Errors.UserError, __name__ + '.' + self.__class__.__name__ + ': exception raised to abort.'
