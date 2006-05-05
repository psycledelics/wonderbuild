#! /usr/bin/env python

###################################################################
###################################################################
###################################################################

sp = SourcePackage(
	name = 'psycle',
	version = [0, 0, 0],
	bug_report = 'bohan.psycle@retropaganda.info'
	origin = 'http://psycle.sourceforge.net'
)

engine = Module(
	name = 'lib-psycle.engine-0',
	type = Module.types.lib,
	version = [0, 0, 0]
)
engine.public_requires.add(
	debian = ['lib-universalis-dev >= 0'],
	pkgconfig = ['universalis >= 0']
)
engine.sources.add(find('src', 'psycle/engine', '*.cpp'))
engine.private_headers.add(find('src', 'psycle/engine', '*.private.hpp.in'))
engine.config_headers.add(find('src', 'psycle/engine', '*.hpp.in'))
engine.public_headers.add(find('src', 'psycle/engine', '*.hpp'))
engine.pkgconfig(
	name = 'psycle.engine',
	description = 'psycle engine library'
)

mp = ModulePackage(
	name = 'psycle.plugins',
	version = [0, 0, 0],
	description = 'psycle plugins'
)
mp.add([psycle.plugin.sine, psycle.plugin.output.default])

bp = BinaryPackage(
	name = 'lib-psycle.plugins',
	description = mp.description,
	long_description =
		sp.long_description +
		"""
			this package contains plugins runtime libraries
		"""
)
bp.add(mp.modules)
bp.files.add(destination = os.path.join(bp.share, 'pixmaps', sp.name), find('pixmaps', '*.xpm', '*.png'))

bp_dev = BinaryPackage(
	name = 'lib-psycle.plugins-dev',
	description = mp.description
	long_description =
		sp.long_description +
		"""
			this package contains development files for the plugins
		"""
)
bp_dev.add([mp.headers, mp.pkgconfigs])

da = DistributionArchive('shell.sourceforge.net:/home/groups/p/ps/psycle/htdocs/packages/debian')
da.add('sid', 'unstable', [sp, bp, bp_dev])

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
	
	def __init__(self, directory, pattern="*"):
		self.stack = [directory]
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
				self.files = os.listdir(self.directory)
				self.index = 0
			else:
				# got a filename
				fullname = os.path.join(self.directory, file)
				if os.path.isdir(fullname): # and not os.path.islink(fullname):
					self.stack.append(fullname)
				if fnmatch.fnmatch(file, self.pattern):
					return fullname

class CompilerFlags:
	__init__(self):
		self.defines = []
		self.optimizations = []
		self.debugging_info = []

class LinkerFlags:
	__init_(self):
		self.optimizations = []

class CPPDefine:
	def __init(name, value = ''):
		seff.name = name
		self.value = value

class File:
	def __init__(self, filename):
		self.filename = filename
		
class Header(File):
	def __init__(self, filename):
		self = File(filename)
		
class Source(Header):
	def __init__(self, filename):
		self = Header(filename)
		self.defines = []
	
class Object:
	def __init__(self, source):
		self.source = source
	
class ModulePackage:
	def __init__(self, name, version = []):
		self.name = name
		self.version = version
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
			result.append(x.public_merged_linker_flags())
		return result
	
	def merged_private_linker_flags(self):
		result = self.linker_flags
		for x in self.public_requires:
			result.append(x.private_merged_linker_flags())
		return result
	
class Module(ModulePackage):
	class Types:
		hpp = 'hpp'
		shared_lib = 'shared_lib'
		static_lib = 'static_lib'
		bin = 'bin'
		python = 'python'
	
	def __init__(self, name, type, version = []):
		self = ModulePackage(name, type, version)
		self.headers = []
		self.sources = []
		self.resources = []
		self.objects = []
	
class BinaryPackage:
	def __init__(self, name):
		self.name = name
		self.binary_version = 0
		self.package_version = 0

class DistributionArchive:
	def __init__(self. remote_path):
		self.remote_path = remote_path
