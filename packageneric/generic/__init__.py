#! /usr/bin/env python

###################################################################
###################################################################
###################################################################

sp = SourcePackage()
sp.name = 'psycle'
sp.version = [0, 0, 0]
sp.bug_report = 'bohan.psycle@retropaganda.info'
sp.origin = 'http://psycle.sourceforge.net'

engine = Module()
engine.name = 'lib-psycle.engine-0'
engine.type = Module.types.lib
engine.version = [0, 0, 0]
engine.public_requires.debian.append('lib-universalis-dev >= 0')
engine.public_requires.pkgconfig.append('universalis >= 0')
engine.sources.add(find('src', 'psycle/engine', '*.cpp'))
engine.private_headers.add(find('src', 'psycle/engine', '*.private.hpp.in'))
engine.config_headers.add(find('src', 'psycle/engine', '*.hpp.in'))
engine.public_headers.add(find('src', 'psycle/engine', '*.hpp'))
engine.pkgconfig.name = 'psycle.engine'
engine.pkgconfig.description = 'psycle engine library'

mp = ModulePackage()
mp.name = 'psycle.plugins'
mp.version = [0, 0, 0]
mp.description = 'psycle plugins'
mp.modules.append(psycle.plugin.sine)
mp.modules.append(psycle.plugin.output.default)

bp = BinaryPackage()
bp.name = 'lib-psycle.plugins',
bp.description = mp.description,
bp.long_description = sp.long_description + "this package contains plugins runtime libraries"
bp.files.append(mp.modules.files())
bp.files.append(find('pixmaps', '*.xpm', '*.png'))

bp_dev = BinaryPackage()
bp_dev.name = 'lib-psycle.plugins-dev',
bp_dev.description = mp.description
bp_dev.long_description = sp.long_description + "			this package contains development files for the plugins"
bp_dev.files.append(mp.headers)
bp_dev.files.append(mp.pkgconfigs)

da = DistributionArchive()
da.remote_path = 'shell.sourceforge.net:/home/groups/p/ps/psycle/htdocs/packages/debian'
da.binary_packages('sid', 'unstable').append([sp, bp, bp_dev])

###################################################################
###################################################################
###################################################################

import os, fnmatch

class EnvList:
	def __init__(self):
		env = Environment()
		dictionary = env.Dictionary()
		keys = dictionary.keys()
		keys.sort()
		for key in keys:
			print '%s = %s' % (key, dictionary[key])

class Find:
	# a forward iterator that traverses a directory tree
	
	def __init__(self, strip_path, path, pattern="*"):
		self.strip_path = strip_path
		self.stack = [path]
		self.pattern = pattern
		self.files = []
		self.index = 0
	
	def __getitem__(self, index):
		while 1:
			try:
				file = self.files[self.index]
				self.index = self.index + 1
			except IndexError:
				# pop next directory from stack
				self.directory = self.stack.pop()
				self.files = os.listdir(os.path.join(self.strip_path, self.directory))
				self.index = 0
			else:
				# got a filename
				path = os.path.join(self.directory, file)
				if os.path.isdir(os.path.join(self.strip_path, path)):
					self.stack.append(path)
				if fnmatch.fnmatch(file, self.pattern):
					return path

class SourcePackage:
	def __init__(self):
		self.name = None
		self.version = []
		self.path = None
		
class CompilerFlags:
	class Define:
		def __init(name, value = ''):
			self.name = name
			self.value = value
	def __init__(self):
		self.defines = []
		self.include_path = []
		self.optimizations = []
		self.debugging_info = []

class LinkerFlags:
	def __init_(self):
		self.library_path = []
		self.optimizations = []

class File:
	def __init__(self):
		self.filename = None
		
class Header(File):
	def __init__(self):
		File.__init__(self)
		
class Source(Header):
	def __init__(self):
		Header.__init__(self)
		self.defines = []
	
class Object:
	def __init__(self):
		self.source = None
	
class ModulePackage:
	def __init__(self):
		self.name = None
		self.version = []
		self.compiler_flags = []
		self.linker_flags = []
		self.public_requires = []
		self.private_requires = []
	
	def merged_compiler_flags(self):
		result = self.compiler_flags
		for x in self.public_requires:
			result.append(x.merged_compiler_flags())
		return result
	
	def merged_public_linker_flags(self):
		result = self.linker_flags
		for x in self.public_requires:
			result.append(x.merged_public_linker_flags())
		return result
	
	def merged_private_linker_flags(self):
		result = self.merged_public_linker_flags()
		for x in self.public_requires:
			result.append(x.merged_private_linker_flags())
		return result
	
class Module(ModulePackage):
	class Types:
		hpp = 'hpp'
		shared_lib = 'shared_lib'
		static_lib = 'static_lib'
		bin = 'bin'
		python = 'python'
	
	def __init__(self, name = None, type = None, version = []):
		ModulePackage.__init__(self)
		self.headers = []
		self.sources = []
		self.resources = []
		self.objects = []
	
class BinaryPackage:
	def __init__(self):
		self.source_package = None
		self.name = None
		self.files = []

class DistributionArchive:
	def __init__(self):
		self.remote_path = None
		self.source_packages = []
		self.binary_packages = []
