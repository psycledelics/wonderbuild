#! /usr/bin/env python

# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006 johan boule <bohan@jabber.org>
# copyright 2006 psycledelics http://psycle.pastnotecut.org

import os, fnmatch
#from SCons.Script.SConscript import SConsEnvironment
#from SCons.Script import *

def pkg_config(context, name, what):
	context.Message('checking for pkg-config --%s %s ... ' % (what, name))
	result = context.TryAction('pkg-config --%s \'%s\'' % (what, name))[0]
	context.Result(result)
	return result
	
def print_all_nodes(dirnode, level = 0):
	"""Print all the scons nodes that are children of this node, recursively."""
	if type(dirnode)==type(''):
		dirnode=Dir(dirnode)
	dt = type(Dir('.'))
	for f in dirnode.all_children():
		if type(f) == dt:
			print "%s%s: .............."%(level * ' ', str(f))
			print_dir(f, level+2)
		print "%s%s"%(level * ' ', str(f))

def Glob(includes = ['*'], excludes = None, dir = '.'):
	"""Similar to glob.glob, except globs SCons nodes, and thus sees generated files and files from build directories.
	Basically, it sees anything SCons knows about.
	A key subtlety is that since this function operates on generated nodes as well as source nodes on the filesystem,
	it needs to be called after builders that generate files you want to include.
	
	It will return both Dir entries and File entries
	"""
	
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
		children = filter(fn_filter, where.all_children(scan=0))
		nodes = []
		for f in children:
			nodes.append(gen_node(f))
		return nodes

	def gen_node(n):
		"""Checks first to see if the node is a file or a dir, then creates the appropriate node.
		(code seems redundant, if the node is a node, then shouldn't it just be left as is?)
		"""
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

class Find:
	"""a forward iterator that traverses a directory tree"""
	
	def __init__(self, strip_path, path, pattern = '*'):
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
				if fnmatch.fnmatchcase(file, self.pattern):
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
				try:
					env[key]
					if len(env[key]):
						print key, '->', env[key], '->', env.subst('$' + key)
					else:
						print key, '<- empty'
				except:
					pass
			show('CPPPATH')
			show('CXXFLAGS')
			show('LIBPATH')
			show('LIBS')
			show('LINKFLAGS')
	
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
		
class Person:
	def __init__(self, name, email = None):
		self.name = name
		self.email = email
		
class SourcePackage:
	def __init__(self, name = None, version = None, path = '.'):
		self.name = name
		if version is None:
			self.version = []
		else:
			self.version = version
		self.path = path
	
class File:
	def __init__(self):
		self.strip_path = None
		self.path = None
		self.install_path = None
	
class SourceFile:
	def __init__(self, path):
		self.path = path
		self.defines = []
		self.include_path = []
	
class ObjectFile:
	def __init__(self, source):
		self.source = source
		self.defines = source.defines
		self.include_path = source.include_path
		self.compiler_flags = None
	
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
		self.libraries = []
		self.optimizations = []
	
class ExternalPackage:
	def __init__(self, env, debian, debian_version_compare, pkg_config = None, pkg_config_version_compare = None):
		self.env = env.Copy()
		self.debian = debian
		self.debian_version_compare = debian_version_compare
		self.pkg_config = pkg_config
		self.pkg_config_version_compare = pkg_config_version_compare
		self.parsed = False
		
	def get_env(self):
		if not self.parsed:
			self.parsed = True
			if not self.pkg_config is None:
				print 'reading config of external package:', self.pkg_config, self.pkg_config_version_compare, '...'
				self.static_libs = self.env.ParseConfig('pkg-config --cflags --libs ' + self.pkg_config) # problem: '>' is interpreted by the shell
		return self.env

	def __str__(self):
		strings = []
		if not self.pkg_config is None:
			strings.append(self.pkg_config)
			if not self.pkg_config_version_compare is None:
				strings.append(' ')
				strings.append(self.pkg_config_version_compare)
		else:
			strings.append(self.debian)
			if not self.debian_version_compare is None:
				strings.append(' ')
				strings.append(self.debian_version_compare)
		string = ''
		for x in strings:
			string += x
		return string
	
	def show(self):
		strings = ['======== module package external: ']
		strings.append(str(self))
		strings.append(' ========')
		string = ''
		for x in strings:
			string += x
		print string
		EnvList(self.get_env())
	
class Module:
	class Types:
		files = 'files'
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
				public_requires += ' ' + str(x)
			debian = ''
			debian_version_compare = ''
			self.env = ExternalPackage(self.env, debian, debian_version_compare, public_requires).get_env()
		return self.env
	
	def show(self):
		print '======== module internal:', self.name, self.version, '========'
		public_requires = []
		for x in self.public_requires:
			public_requires.append(str(x))
		print 'requires', public_requires
		EnvList(self.get_env())
		
	def scons(self):
		return self.get_env().SharedLibrary(self.name, self.sources)

class Package:
	pass

class DebianPackage:
	def __init__(self):
		self.source_package = None
		self.name = None
		self.section = self.source_package.section
		self.architecture = 'any'
		self.provides = []
		self.depends = []
		self.recommends = []
		self.suggests = []
		self.description = None
		self.long_description = None
		self.files = []

class Debian:
	def __init_(self):
		self.source_package = None
		self.section = 'libs'
		self.priority = 'optional'
		self.maintainer = None
		self.uploaders = []
		self.build_depends = []
		self.binary_packages = []
		self.description = None

	def	get_build_depends(self):
		result = self.build_depends
		for x in self.binary_packages:
			for xx in x.build_depends:
				if not xx in self.build_depends:
					result.append(xx)
					
	def control(self, where):
		def out(*strings):
			print strings
		out('Source: ', self.source_package.name, '\n')
		out('Section: ', self.section, '\n')
		out('Priority: ', self.priority, '\n')
		out('Build-Depends: ')
		for x in self.get_build_depends():
			 out(x.name, ' (', x.version_compare, '), ')
		out('\n')
		out('Maintainer', self.maintainer)
		out('Uploaders: ')
		for x in self.uploaders:
			out(x.name, ' <', x.email, '>, ')
		out('\n')
		out('Standards-Version: 3.6.2\n')
		for x in self.binary_packages:
			out('Package: ', x.name, '\n')
			out('Provides: ')
			for xx in x.provides:
				out(xx, ', ')
			out('\n')
			out('Suggests: ')
			for xx in x.suggests:
				out(xx.name, ' (', xx.version_compare, '), ')
			out('\n')
			out('Recommends: ')
			for xx in x.recommends:
				out(xx.name, ' (', xx.version_compare, '), ')
			out('\n')
			out('Depends: ')
			for xx in x.depends:
				out(xx.name, ' (', xx.version_compare, '), ')
			out('\n')
			out('Section: ')
			if x.section is None:
				out(self.section)
			else:
				out(x.section)
			out('\n')
			out('Architecture: ', x.architecture, '\n')
			out('Description', x.description, '\n')
			for xx in self.description:
				if xx == '':
					out('.')
				else:
					out(' ')
				out(xx, '\n')
			out('.\n')
			for xx in x.long_description:
				if xx == '':
					out('.')
				else:
					out(' ')
				out(xx, '\n')
			out('\n')
		
class DistributionArchive:
	def __init__(self):
		self.remote_path = None
		self.source_packages = []
		self.binary_packages = []
