# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006 johan boule <bohan@jabber.org>
# copyright 2006 psycledelics http://psycle.pastnotecut.org

import sys, os.path
from tty_font import tty_font

class project:

	def __init__(self, name):
		self._check_scons_and_python_versions()
		self._name = name
		if not self.is_subscript():
			import packageneric.generic.scons
			self.information('version of packageneric is ' + str(packageneric.generic.scons.version()))
		self.information('=============================================')
		self.information('  project name is ' + self.name())
		self._scons()
		self.information('=============================================')

	def name(self): return self._name
	
	def subscript(self, path):
		self._subscript_stack().append(self)
		try:
			try: results = self.__class__._subscript_results
			except AttributeError: results = self.__class__._subscript_results = {}
			key = self._scons().File(path).get_abspath()
			try: result = results[key]
			except KeyError:
				self.information('subscript ' + path)
				result = results[key] = self._scons().SConscript(path) # SConscriptChDir(False) ; SConscript(path, src_dir, build_dir) ; SConscriptChDir(True)
				self.trace('subscript stack pop: ' + ' -> '.join([project.name() for project in self._subscript_stack()]))
		finally: self._subscript_stack().pop()
		return result

	def is_subscript(self):
		if len(self._subscript_stack()): return True
		return False

	def _subscript_stack(self):
		try: return self.__class__._subscript_stack_
		except AttributeError:
			self.__class__._subscript_stack_ = []
			return self.__class__._subscript_stack_

	def builders(self):
		try: return self._builders
		except AttributeError:
			self._builders = []
			return self._builders
	def add_builder(self, builder):
		self.builders().append(builder)
		self.trace('added builder ' + builder.name() + ': ' + ' '.join(builder.alias_names()))

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
		scons.Alias('packageneric:install-runtime',
			[
				os.path.join('$packageneric__install__stage_destination', '$packageneric__install__bin'),
				os.path.join('$packageneric__install__stage_destination', '$packageneric__install__lib'),
				os.path.join('$packageneric__install__stage_destination', '$packageneric__install__lib_exec'),
				os.path.join('$packageneric__install__stage_destination', '$packageneric__install__share'),
				os.path.join('$packageneric__install__stage_destination', '$packageneric__install__var'),
				os.path.join('$packageneric__install__stage_destination', '$packageneric__install__etc')
			]
		)
		scons.Alias('packageneric:install-dev',
			[
				os.path.join('$packageneric__install__stage_destination', '$packageneric__install__include')
			]
		)
		scons.Alias('packageneric:install',
			[
				'packageneric:install-runtime',
				'packageneric:install-dev'
			]
		)
		scons.Default('packageneric:install')
		#scons.Default('$packageneric__install__stage_destination')
	
	def command_line_arguments(self):
		try: return self._command_line_arguments
		except AttributeError:
			import SCons.Script
			self._command_line_arguments = SCons.Script.ARGUMENTS
			return self._command_line_arguments
		
	def packageneric_directory(self):
		import packageneric
		return packageneric.__path__[0]
	
	def source_dir(self):
		try: return self._source_dir
		except AttributeError:
			self._source_dir = self._scons().Dir('.').get_abspath()
			return self._source_dir

	def build_dir(self):
		try: return self._build_dir
		except AttributeError:
			self._build_dir = self._scons().Dir('$packageneric__build_dir').get_abspath()
			return self._build_dir

	def build_variant(self):
		try: return self._build_variant
		except AttributeError:
			self._build_variant = self._scons().subst('$packageneric__build_variant')
			return self._build_variant

	def build_variant_intermediate_dir(self):
		try: return self._build_variant_intermediate_dir
		except AttributeError:
			self._build_variant_intermediate_dir = self._scons().Dir(self._build_variant_intermediate_dir_with_scons_vars()).path
			return self._build_variant_intermediate_dir

	def check_dir(self):
		try: return self._check_dir
		except AttributeError:
			self._check_dir = self._scons().Dir(os.path.join(self.build_variant_intermediate_dir(), 'checks')).path
			return self._check_dir

	def check_log(self):
		try: return self._check_log
		except AttributeError:
			self._check_log = self._scons().File(self.check_dir() + '.log').path
			return self._check_log

	def intermediate_target_dir(self):
		try: return self._intermediate_target_dir
		except AttributeError:
			self._intermediate_target_dir = self._scons().Dir(os.path.join(self.build_variant_intermediate_dir(), 'source-twin-targets')).path
			return self._intermediate_target_dir

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
			#self.trace('creating build env')
			import contexes
			self._contexes = contexes.template(self.env_class())(self)
			chain = self._contexes.build()
			chain.compilers().cxx().command().set('$packageneric__cxx_compiler')
			chain.linker().command().set('$packageneric__linker') # todo SMARTLINK for C++ vs C
			scons = self._scons()
			self.trace('c++ compiler is ' + scons.subst('$CXX') + ' version ' + scons.subst('$CXXVERSION'))
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
			chain.compilers().cxx().paths().add([os.path.join(self.build_variant_intermediate_dir(), 'project', 'src')])
			scons.FileFromValue(
				os.path.join(self.build_variant_intermediate_dir(), 'project', 'src', 'packageneric', 'configuration.private.hpp'),
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
			for i in find(self, '.', '.', '*.hpp.in'):
				self.trace(i.relative())
				scons.SubstitutedFile(
					os.path.join(self.intermediate_target_dir(), i.strip(), os.path.splitext(i.relative())[0]),
					i.full()
				)
			self._contexes.client().uninstalled().linker().paths().add([self.intermediate_target_dir()])
			self._contexes.client().installed().compilers().cxx().paths().add(['$packageneric__install__include'])
			self._contexes.client().installed().linker().paths().add(['$packageneric__install__lib'])
			return self._contexes
			
	def _scons(self):
		try: return self._scons_
		except AttributeError:
			import SCons.Environment
			scons = self._scons_ = SCons.Environment.Environment()
			scons.Default() # todo only for root scons?
			import SCons.Tool
			toolpath = [os.path.join(self.packageneric_directory(), 'generic', 'scons', 'tools')]
			SCons.Tool.Tool('file_from_value', toolpath = toolpath)(scons)
			SCons.Tool.Tool('substituted_file', toolpath = toolpath)(scons)
			scons.SourceCode('.', None) # we don't use the default source code fetchers (RCS, SCCS ...), so we disable them to avoid uneeded processing
			scons.SetOption('implicit_cache', True)
			#scons.SourceSignatures('timestamp') # scons 0.96.92.0002 bugs with timestamps of symlinks, or even, always ignores all changes!
			scons.SourceSignatures('MD5')
			scons.TargetSignatures('build')
			#scons.TargetSignatures('content')
			self._options()
			# Below are settings which depend on self._options(), that we just called above
			if not self.is_subscript():
				scons.Help(self._options().GenerateHelpText(scons))
				# Below are settings which depend on self.options(), that we just called above
				cache = os.path.join(self.build_dir(), 'cache')
				self.information('     cache dir is ' + scons.Dir(cache).path)
				scons.CacheDir(cache)
				signature = os.path.join(self.build_dir(), 'signatures')
				self.information('signature file is ' + scons.Dir(signature).path)
				scons.SConsignFile(signature)
			scons.BuildDir(self.intermediate_target_dir(), self.source_dir(), duplicate = False)
			scons['INSTALLSTR'] = self.message('packageneric: ', 'linking file $TARGET', font = '1;35')
			return self._scons_

	def _build_variant_dir_with_scons_vars(self): return os.path.join('$packageneric__build_dir', 'variants', '$packageneric__build_variant')
	def _build_variant_intermediate_dir_with_scons_vars(self): return os.path.join(self._build_variant_dir_with_scons_vars(), 'intermediate', self.name())
	def _build_variant_install_dir_with_scons_vars(self): return os.path.join(self._build_variant_dir_with_scons_vars(), 'stage-install')

	def _options(self):
		try: return self._options_
		except AttributeError:
			scons = self._scons()

			try: build_dir = self.command_line_arguments()['packageneric__build_dir']
			except KeyError: build_dir = os.path.join(scons.GetLaunchDir(), '++packageneric')
			scons['packageneric__build_dir'] = build_dir

			try: build_variant = self.command_line_arguments()['packageneric__build_variant']
			except KeyError: build_variant = 'default'
			scons['packageneric__build_variant'] = build_variant

			try: options_file_path = self.command_line_arguments()['packageneric__options']
			except KeyError: options_file_path = scons.File(os.path.join(scons.subst(self._build_variant_dir_with_scons_vars()), 'options')).get_abspath()
			self.information('  options file is ' + options_file_path)

			import SCons.Options
			class options(SCons.Options.Options):
				def GenerateHelpText(self, env, sort=None):
					if sort:
						options = self.options[:]
						options.sort(lambda x,y,func=sort: func(x.key,y.key))
					else:
						options = self.options

					def format(opt, self=self, env=env):
						if env.has_key(opt.key):
							actual_no_subst = env[opt.key].replace('$', '$$')
							actual_subst = env.subst('${%s}' % opt.key)
						else:
							actual_no_subst = None
							actual_subst = None
						if opt.default is None:
							default_no_subst = None
						else:
							default_no_subst = opt.default.replace('$', '$$')
						result = '%s: %s' % (opt.key, opt.help)
						if default_no_subst is not None:
							result += '\n    default: %s' % default_no_subst
							if default_no_subst != opt.default: result += ' -> %s' % opt.default
						if actual_no_subst != default_no_subst:
							result += '\n     actual: %s' % actual_no_subst
							if actual_no_subst != actual_subst: result += ' -> %s' % actual_subst
						result += '\n'
						return result
					return \
						'\n' \
						'========================================\n' \
						'========= packageneric options =========\n' \
						'========================================\n' \
						'\n' + \
						'\n'.join([format(option) for option in options])

			self._options_ = options(options_file_path, self.command_line_arguments())
			self._options_.AddOptions(
				# todo change underscores to colons and hypens since variables can be referred to as ${packageneric:build-dir}
				#('packageneric:build-dir', 'directory where to build into'),
				('packageneric__build_dir', 'directory where to build into'),
				('packageneric__install__stage_destination', 'directory to install under (stage installation)', self._build_variant_install_dir_with_scons_vars()),
				('packageneric__build_variant', 'subdirectory where to build into'),
				#('packageneric__install__prefix', 'directory to install under (final installation)', os.path.join('/', 'opt', self.name())),
				('packageneric__install__prefix', 'directory to install under (final installation)', os.path.join('/', 'usr', 'local')),
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
				('packageneric__verbose', '(0|1) set to 1 for build verbiage', '0'),
				('packageneric__debug', '(0|1) set to 1 to build for debugging', '0'),
				('packageneric__test', '(0|1) set to 1 to perform unit tests', '1')
			)
			self._options_.Update(scons)
			self.information('    source dir is ' + self.source_dir())
			self.information('     build dir is ' + self.build_dir())
			if scons.Dir(self.build_dir()).get_abspath() == scons.Dir(self.source_dir()).get_abspath():
				self.abort(
					'source and build directories are the same.\n' +
					'please choose a build dir separate from the source dir so that the latter is not polluted with derived files.'
				)
			self.information(' build variant is ' + scons.subst('$packageneric__build_variant'))
			for path in [os.path.split(options_file_path)[0]] + [
					scons.subst(path) for path in
					(
						os.path.join('$packageneric__install__stage_destination', '$packageneric__install__bin'),
						os.path.join('$packageneric__install__stage_destination', '$packageneric__install__lib'),
						os.path.join('$packageneric__install__stage_destination', '$packageneric__install__lib_exec'),
						os.path.join('$packageneric__install__stage_destination', '$packageneric__install__include'),
						os.path.join('$packageneric__install__stage_destination', '$packageneric__install__share'),
						os.path.join('$packageneric__install__stage_destination', '$packageneric__install__var'),
						os.path.join('$packageneric__install__stage_destination', '$packageneric__install__etc')
					)
			]: SCons.Options.PathOption.PathIsDirCreate('', path, scons)
			self._options_.Save(options_file_path, scons)
			return self._options_

	def _check_scons_and_python_versions(self):
		scons_version = 0, 96, 92
		python_version = 2, 3
		# We do a rather painful check to be sure a user having very old versions isn't left with an uncomprehensible error message.
		import SCons.Script
		try: SCons.Script.EnsureSConsVersion(*scons_version)
		except SystemExit: raise
		except:
			# If it failed with an AttributeError, this means we have a pre 0.96.91 or so version, where the EnsureSConsVersion function cannot be called directly.
			# If it failed with a TypeError, it's because the EnsureSConsVersion can only handle two numbers for the version.
			# We call again the EnsureSConsVersion function through the default environment.
			# This will fail too, but this time with a nice error message.
			try:
				import SCons.Defaults ; env = SCons.Defaults.DefaultEnvironment()
				env.EnsureSConsVersion(*scons_version[0:1]) # first try with only the first two numbers
				try: env.EnsureSConsVersion(*scons_version) # then with all the numbers
				except TypeError: env.EnsureSConsVersion(0, 97) # get rid of all old versions
			except SystemExit: raise
			except: # if python doesn't understand the syntax or something, we print a message suggesting to upgrade it
				print 'SCons version and/or python version are too old.'
				print 'The lowest version of SCons that is known to work is', str(scons_version)
				print 'The lowest version of python that is known to work is', str(python_version)
				import sys
				sys.exit(2)
		SCons.Script.EnsurePythonVersion(*python_version)

	###########################	
	######### logging #########

	import SCons.Script.Main
	_progress_display_ = SCons.Script.Main.progress_display
	def _progress_display(message): project._progress_display_(message)
	SCons.Script.Main.progress_display = _progress_display
	
	def progress(self): # todo progress is not counted yet.. it would be nice for lengthy builds
		try: todo = self.__class__._progress_todo
		except AttributeError: todo = 0
		try: done = self.__class__._progress_done
		except AttributeError: done = 0
		return str(done) + '/' + str(todo)
	
	def progress_add_todo(self, count = 1):
		try: self.__class__._progress_todo += count
		except AttributeError: self.__class__._progress_todo = count

	def progress_add_done(self, count = 1):
		try: self.__class__._progress_done += count
		except AttributeError: self.__class__._progress_done = count

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

	def _log(self, message):
		'honors scons -Q option'
		import SCons.Script.Main
		SCons.Script.Main.progress_display(message)

	def _log_always(self, message): print message

	def trace(self, message): self._log(self.message('packageneric: trace: ', message, font = '2;33'))
		
	def information(self, message): self._log(self.message('packageneric: information: ', message, font = '2;34'))
	
	def success(self, message): self._log(self.message('packageneric: success: ', message, font = '32'))
		
	def warning(self, message): self._log_always(self.message('packageneric: warning: ', message, font = '1;35'))
	
	def error(self, message): self._log_always(self.message('packageneric: error: ', message, font = '1;31'))

	def abort(self, message):
		self._log_always(self.message('packageneric: error: ', message, font = '31'))
		self.error('bailing out.')
		import SCons.Errors
		raise SCons.Errors.UserError, __name__ + '.' + self.__class__.__name__ + ': exception raised to abort.'
