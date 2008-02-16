# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

import sys, os.path
from tty_font import tty_font

class project:

	def __init__(self, name, default_build_dir = None):
		self.root()
		self._name = name
		self.information('=============================================')
		self.information('  project name is ' + self.name())
		self._scons()
		self.information('=============================================')

	def name(self): return self._name

	def root(self):
		try: return self.__class__._root
		except AttributeError:
			from project_root import project_root
			self.__class__._root = project_root(self)
			return self.__class__._root
				
	def subscript(self, path): return self.root().subscript(self, path)
	def default_targets(self, builders): self.root().default_targets(builders)
	def command_line_targets(self): return self.root().command_line_targets()
	def command_line_arguments(self): return self.root().command_line_arguments()

	def add_builder(self, x): pass
		
	def source_dir(self):
		try: return self._source_dir
		except AttributeError:
			self._source_dir = self._scons().Dir('.').get_abspath()
			return self._source_dir

	def packageneric_dir(self): return self.root().packageneric_dir()
	def build_dir(self): return self.root().build_dir()
	def build_variant(self): return self.root().build_variant()

	def build_variant_intermediate_dir(self):
		try: return self._build_variant_intermediate_dir
		except AttributeError:
			self._build_variant_intermediate_dir = os.path.join(self.root()._build_variant_dir(), 'intermediate', self.name())
			return self._build_variant_intermediate_dir

	def check_dir(self):
		try: return self._check_dir
		except AttributeError:
			self._check_dir = os.path.join(self.build_variant_intermediate_dir(), 'checks')
			return self._check_dir

	def check_log(self):
		try: return self._check_log
		except AttributeError:
			self._check_log = self.check_dir() + '.log'
			return self._check_log

	def intermediate_target_dir(self):
		try: return self._intermediate_target_dir
		except AttributeError:
			self._intermediate_target_dir = os.path.join(self.build_variant_intermediate_dir(), 'source-twin-targets')
			return self._intermediate_target_dir

	def platform(self): return self.root().platform()
	def platform_executable_format(self): return self.root().platform_executable_format()
	def env_class(self): return self.root().env_class()
		
	def contexes(self):
		try: return self._contexes
		except AttributeError:
			contexes = self._contexes = self.root().contexes()
			contexes.build().compilers().cxx().paths().add([os.path.join(self.build_variant_intermediate_dir(), 'project', 'src')])
			contexes.build().compilers().cxx().defines().add({'PACKAGENERIC': None}) # todo make that shared amongst projects
			scons = self._scons()
			self.file_from_value( # todo make that shared amongst projects
				os.path.join('project', 'src', 'packageneric', 'configuration.private.hpp'),
				''.join(['#define PACKAGENERIC__CONFIGURATION__%s %s\n' % (n, v) for n, v in
					[('INSTALL_PATH__BIN_TO_%s' % n, '"%s"' % v) for n, v in
						('LIB', '../lib'), # todo from options, function to compute a relative path
						('SHARE', '../share'), # todo from options, function to compute a relative path
						('VAR', '../var'), # todo from options, function to compute a relative path
						('ETC', '../etc') # todo from options, function to compute a relative path
					] +
					[('COMPILER__HOST', '"' + scons.subst('$CXX') + ' version ' + scons.subst('$CXXVERSION') + '"')]
				])
			)
			from find import find
			for i in find(self, self.source_dir(), ['*.hpp.in']):
				self.trace(i.relative())
				#self.trace(os.path.join('/a', '/b')) <-- beware that the result is '/b'
				self._scons().SubstitutedFile(
					os.path.join(self.intermediate_target_dir(), os.path.splitext(i.relative())[0]),
					i.full()
				)
			return self._contexes

	def file_from_value(self, file_path, value): return self._scons().FileFromValue(os.path.join(self.build_variant_intermediate_dir(), file_path), value)[0].path
	#def substituted_file(self, file_path): return self._scons().SubstitutedFile(os.path.join(self.intermediate_target_dir(), file_path)...
	
	def _scons(self):
		try: return self._scons_
		except AttributeError:
			scons = self._scons_ = self.root()._scons()
			self.information('    source dir is ' + self.source_dir())
			scons.SourceCode(self.source_dir(), None) # we don't use the default source code fetchers (RCS, SCCS ...), so we disable them to avoid uneeded processing
			scons.BuildDir(self.intermediate_target_dir(), self.source_dir(), duplicate = False) # This allows source files to referenced as is they where in the build dir.
			return self._scons_

	def _options(self): return self.root()._options()

	###########################	
	######### logging #########

	def progress(self): return self.root().progress()
	def progress_add_todo(self, count = 1): self.root().progress_add_todo(count)
	def progress_add_done(self, count = 1): self.root().progress_add_done(count)
	def message(self, prefix, message, font = None): return self.root().message(prefix + self.name() + ': ', message, font)
	def trace(self, message): self.root().trace(message)
	def information(self, message): self.root().information(message)
	def success(self, message): self.root().success(message)		
	def warning(self, message): self.root().warning(message)
	def error(self, message): self.root().error(message)
	def abort(self, message): self.root().abort(message)
