#! /usr/bin/env python

# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006 johan boule <bohan@jabber.org>
# copyright 2006 psycledelics http://psycle.pastnotecut.org

import os, fnmatch
#from SCons.Script.SConscript import SConsEnvironment
#from SCons.Script import *

def pkg_config_check(context, name):
	 context.Message('checking for %s ... ' % name)
	 result = context.TryAction('pkg-config --exists \'%s\'' % name)[0]
	 context.Result(result)
	 return result

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
				
class EnvList:
	def __init__(self, env, all = False):
		if all:
			dictionary = env.Dictionary()
			keys = dictionary.keys()
			keys.sort()
			for key in keys:
				print '%s = %s' % (key, dictionary[key])
		else:
			def show(key):
				if len(env[key]):
					print key, '->', env[key], '->', env.subst('$' + key)
				else:
					print key, '<- empty'
			show('CPPPATH')
			show('CXXFLAGS')
			show('LIBPATH')
			show('LIBS')
			show('LINKFLAGS')
			
class ExternalModulePackage:
	def __init__(self, env, requires):
		self.env = env.Copy()
		self.requires = requires
		self.parsed = False
		
	def get_env(self):
		if not self.parsed:
			self.parsed = True
			print 'reading config of external package:', self.requires, '...'
			self.static_libs = self.env.ParseConfig('pkg-config --cflags --libs ' + self.requires)
		return self.env
	
	def show(self):
		print '======== module package external:', self.requires, '========'
		EnvList(self.get_env())
		
class InternalModule:
	class Types:
		hpp = 'hpp'
		shared_lib = 'shared_lib'
		static_lib = 'static_lib'
		bin = 'bin'
		python = 'python'
		
	def __init__(self, env, name = None):
		self.env = env.Copy()
		self.name = name
		self.version = []
		self.public_requires = []
		self.parsed = False
		self.sources = []
		self.headers = []
		
	def get_name(self):
		return self.name
	
	def get_version(self):
		return self.version
	
	def get_sources(self):
		return self.sources
	def add_source(self, source):
		self.sources.append(source)
	def add_sources(self, sources):
		for x in sources: self.add_source(x)
		
	def get_headers(self):
		return self.headers
	def add_header(self, header):
		self.headers.append(header)
	def add_headers(self, headers):
		for x in headers: self.add_header(x)
		
	def get_public_requires(self):
		return self.public_requires
	def add_public_requires(self, requires):
		self.public_requires.append(requires)
		
	def get_env(self):
		if not self.parsed:
			self.parsed = True
			public_requires = ''
			for x in self.public_requires:
				public_requires += ' ' + x.requires
			self.env = ExternalModulePackage(self.env, public_requires).get_env()
		return self.env
	
	def show(self):
		print '======== module internal:', self.name, self.version, '========'
		public_requires = []
		for x in self.public_requires:
			public_requires.append(x.requires)
		print 'requires', public_requires
		EnvList(self.get_env())
		
	def scons(self):
		return self.get_env().SharedLibrary(self.name, self.sources)
	
class InstallPrefix:
	def __init__(self, env):
		# Get our configuration options:
		opts = env.Options('packageneric.configuration')
		opts.Add(env.PathOption('PREFIX', 'Directory to install under', '/usr/local'))
		opts.Update(env)
		# Save, so user doesn't have to specify PREFIX every time
		opts.Save('packageneric.configuration', env)
		env.Help(opts.GenerateHelpText(env))
		# Here are our installation paths:
		self.prefix  = '$PREFIX'
		self.lib     = '$PREFIX/lib'
		self.bin     = '$PREFIX/bin'
		self.include = '$PREFIX/include'
		self.data    = '$PREFIX/share'
		env.Export('env self.prefix self.lib self.bin self.include self.data')
		
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
