#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

class Contexes(object):
	def check_and_build(self):
		'when performing build checks, or building the sources'
		pass
		
	def build(self):
		'when building the sources'
		pass
		
	class client:
		'when used as a dependency'
		pass

class Cmd(object):
	def __init__(self, cmd)
		self.cmd = cmd

	def run(self):
		exec_subprocess(cmd)

class Cxx(Cmd):
	def __init__(self, cmd = 'c++'):
		Cmd.__init__(self, cmd)
		self.paths = []
		self.debug = False
		self.pic = False

	def run(self, source, target):
		args = [self.cmd, '-o', source.path, target.path]
		for i in self.paths: args += ['-I', i.path]
		if self.debug: args.append('-g')
		if self.pic: args.append('-fPIC')
		Cxx.run(self, args)

class GnuCxx(Cxx):
	def __init__(self, cmd = 'g++'):
		Cxx.__init__(self, cmd)
		self.env_vars = ['CPATH', 'CXXFLAGS']

class MsCxx(Cxx):
	def __init__(self):
		Cxx.__init__(self, 'cl')

	def run(self):
		args = [self.cmd, '-nologo', '-Fo', self.output.path, self.input.path]
		Cxx.run(self, args)

class Archiver(Cmd):
	def __init__(self, cmd = 'ar'):
		Cmd.__init__(self, cmd)

class GnuArchiver(Archiver): pass

class MsArchiver(Archiver):
	def __init__(self):
		Archiver.__init__(self, 'lib')

class ArchiveIndexer(Cmd):
	def __init__(self, cmd = 'ranlib'):
		Cmd.__init__(self, cmd)

class GnuArchiveIndexer(ArchiveIndexer): pass

class MsArchiveIndexer(ArchiveIndexer):
	def __init__(self):
		ArchiveIndexer.__init__(self, None)

class Linker(Cmd):
	def __init__(self, cmd = 'ld'):
		Cmd.__init__(self, cmd)

class GnuLinker(Linker): pass

class MsLinker(Linker): pass
	def __init__(self):
		Cmd.__init__(self, 'link')

class Chain(object):
	def __init__(self, compilers = None, archiver = None, archive_indexer = None, linker = None):
		if compilers is None:
			self._compilers = object()
			setattr(self._compilers.__class__, 'cxx', GnuCxx())
		else self._compilers = compilers
		
		if archiver is None: self._archiver = Archiver()
		else: self._archiver = archiver
		
		if archive_indexer is None: self._archive_indexer = ArchiveIndexer()
		else: self._archive_indexer = archive_indexer
		
		if linker is None: self._linker = GnuLinker()
		else: self._linker = linker

class Obj(object):
	def __init__(self, source, compiler, target):
		self.source = source
		self.compiler = compiler
		self.target = target
		
	def run(self):
		self.compiler.run(source, target)
		
class Module(object):
	def __init__(self, sources, chain, target):
		self.sources = sources
		self.chain = chain
		self.target = target
	
	def run(self):
		has_changed = False
		objs = []
		for source in self.sources:
			if source.has_changed():
				has_changed = True
				o = Obj(source, self.chain.cxx, source.change_ext('cpp', 'o'))
				objs.append(o)
				o.run()
		if has_changed:
			self.chain.linker.run(objs, self.target)

