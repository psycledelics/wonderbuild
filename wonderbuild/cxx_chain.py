#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os

from signature import Sig, raw_to_hexstring
from logger import is_debug, debug
from task import Task, exec_subprocess

class Conf(object):
	def __init__(self, project):
		self.project = project
		
	@property
	def sig(self): pass

	@property
	def args(self): pass

class PkgConf(Conf):
	def __init__(self, project):
		Conf.__init__(self, project)
		self.project = project
		self.prog = 'pkg-config'
		self.pkgs = []
		self.flags = []

	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			sig = Sig()
			sig.update(os.environ.get('PKG_CONFIG_PATH', None))
			sig.update(self.prog)
			sig.update(self.flags)
			for p in self.pkgs: sig.update(p)
			sig = self._sig = sig.digest()
			return sig

	@property
	def args(self): return self.compiler_args + self.lib_args

	@property
	def compiler_args(self):
		try: return self._compiler_args
		except AttributeError:
			r, out = exec_subprocess([self.prog, '--cflags'] + self.flags + self.pkgs)
			if r != 0: raise Exception, r
			self._compiler_args = args
			return args

	@property
	def lib_args(self):
		try: return self._lib_args
		except AttributeError:
			r, out = exec_subprocess([self.prog, '--libs'] + self.flags + self.pkgs)
			if r != 0: raise Exception, r
			self._lib_args = args
			return args
	
class ObjConf(Conf):
	def __init__(self, project):
		Conf.__init__(self, project)
		self.prog = 'c++'
		flags = os.environ.get('CXXFLAGS', None)
		if flags is None: self.flags = []
		else: self.flags = flags.split()
		self.pkgs = []
		self.paths = []
		self.defines = {}
		self.debug = False
		self.optim = None
		self.pic = True

	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			sig = Sig()
			sig.update(os.environ.get('CPATH', None))
			sig.update(os.environ.get('CPLUS_INCLUDE_PATH', None))
			for p in self.pkgs: sig.update(p.sig)
			for p in self.paths: sig.update(p.sig)
			for f in self.flags: sig.update(f)
			sig.update(self.shared)
			sig = self._sig = sig.digest()
			return sig

	@property
	def args(self):
		try: return self._args
		except AttributeError:
			args = [self.prog, '-o', None, None, '-c', '-pipe']
			for p in self.pkgs: args += p.compiler_args
			for p in self.paths: args += ['-I', p.path]
			for k, v in self.defines.iteritems():
				if v is None: args.append('-D' + k)
				else: args.append('-D' + k + '=' + v)
			if self.debug: args.append('-g')
			if self.optim is not None: args.append('-O' + str(self.optim))
			if self.pic: args.append('-fPIC')
			args += self.flags
			self._args = args
			return args

	def dyn_args(self, target, source):
		args = self.args[:]
		args[2] = target.path
		args[3] = source.path
		return args
			
class Obj(Task):
	def __init__(self, obj_conf):
		Task.__init__(self, obj_conf.project)
		self.conf = obj_conf
		self.source = None
		self.target = None
		
	@property
	def uid(self):
		try: return self._uid
		except AttributeError:
			sig = self._uid = Sig(self.target.path).digest()
			return sig

	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			sig = self._sig = self.source.sig_to_string()
			return sig
		
	def process(self):
		self.target.parent.make_dir()
		args = self.conf.dyn_args(self.target, self.source)
		r, out, err = exec_subprocess(args)
		if r != 0: raise Exception, r

class LibConf(Conf):
	def __init__(self, obj_conf):
		Conf.__init__(self, obj_conf.project)
		self.obj_conf = obj_conf
		self.prog = obj_conf.prog
		flags = os.environ.get('LDFLAGS', None)
		if flags is None: self.flags = []
		else: self.flags = flags.split()
		self.pkgs = obj_conf.pkgs
		self.paths = []
		self.libs = []
		self.static_libs = []
		self.shared_libs = []
		self.shared = obj_conf.pic

	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			sig = Sig()
			for p in self.pkgs: sig.update(p.sig)
			for p in self.paths: sig.update(p.sig)
			for l in self.libs: sig.update(l)
			for l in self.static_libs: sig.update(l)
			for l in self.shared_libs: sig.update(l)
			for f in self.flags: sig.update(f)
			sig = self._sig = sig.digest()
			return sig

	@property
	def args(self):
		try: return self._args
		except AttributeError:
			args = [self.prog, '-o', None, []]
			for p in self.pkgs: args += p.lib_args
			for p in self.paths: args += ['-L', p.path]
			for l in self.libs: args.append('-l' + l)
			if len(self.static_libs):
				args.append('-Wl,-Bstatic')
				for l in self.static_libs: args.append('-l' + l)
			if len(self.static_libs):
				args.append('-Wl,-Bdynamic')
				for l in self.static_libs: args.append('-l' + l)
			if self.shared: args.append('-shared')
			args += self.flags
			self._args = args
			return args

	def dyn_args(self, target, sources):
		args = self.args[:]
		args[2] = target.path
		args[3] = [s.path for s in sources]
		args = args[:3] + args[3] + args[4:]
		return args

class Lib(Task):
	def __init__(self, lib_conf, aliases = None):
		Task.__init__(self, lib_conf.project, aliases)
		self.conf = lib_conf
		self.obj_conf = self.conf.obj_conf
		self.obj_conf.pic = self.conf.shared
		self.sources = []

	@property
	def uid(self):
		try: return self._uid
		except AttributeError:
			sig = self._uid = Sig(self.target.path).digest()
			return sig

	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			sig = Sig()
			for t in self.in_tasks: sig.update(t.sig)
			ts = [t.target for t in self.in_tasks]
			for s in self.sources:
				if not s in ts: sig.update(s.sig_to_string())
			sig = self._sig = sig.digest()
			return sig

	def process(self):
		args = self.conf.dyn_args(self.target, self.sources)
		r, out, err = exec_subprocess(args)
		if r != 0: raise Exception, r
		
	def new_obj(self, source): return LibObj(self, source)

class LibObj(Obj):
	def __init__(self, lib, source):
		Obj.__init__(self, lib.obj_conf)
		self.source = source
		self.target = lib.target.parent.rel_node(source.path[:source.path.rfind('.')] + '.o')
		self.add_out_task(lib)
		lib.sources.append(self.target)

if False:
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
		def __init__(self, cmd):
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

	class MsLinker(Linker):
		def __init__(self):
			Cmd.__init__(self, 'link')

	class Chain(object):
		def __init__(self, compilers = None, archiver = None, archive_indexer = None, linker = None):
			if compilers is None:
				self._compilers = object()
				setattr(self._compilers.__class__, 'cxx', GnuCxx())
			else: self._compilers = compilers
		
			if archiver is None: self._archiver = Archiver()
			else: self._archiver = archiver
		
			if archive_indexer is None: self._archive_indexer = ArchiveIndexer()
			else: self._archive_indexer = archive_indexer
		
			if linker is None: self._linker = GnuLinker()
			else: self._linker = linker
