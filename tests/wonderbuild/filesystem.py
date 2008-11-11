#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

SAVED_ATTRS = 'root srcnode bldnode node_sigs node_deps raw_deps task_sigs id_nodes'.split()
"Build class members to save"

class BuildContext(object):
	"holds the dependency tree"
	def __init__(self):

		# there should be only one build dir in use at a time
		global bld
		bld = self

		self.task_manager = Task.TaskManager()

		# instead of hashing the nodes, we assign them a unique id when they are created
		self.id_nodes = 0

		# map names to environments, the 'default' must be defined
		self.all_envs = {}

		# ======================================= #
		# code for reading the scripts

		# project build directory - do not reset() from load_dirs()
		self.bdir = ''

		# the current directory from which the code is run
		# the folder changes everytime a wscript is read
		self.path = None

		# ======================================= #
		# cache variables

		# local cache for absolute paths - cache_node_abspath[variant][node]
		self.cache_node_abspath = {}

		# list of folders that are already scanned
		# so that we do not need to stat them one more time
		self.cache_scanned_folders = {}

		# list of targets to uninstall for removing the empty folders after uninstalling
		self.uninstall = []

		# ======================================= #
		# tasks and objects

		# build dir variants (release, debug, ..)
		for v in 'cache_node_abspath task_sigs node_deps raw_deps node_sigs'.split():
			var = {}
			setattr(self, v, var)

		self.cache_dir_contents = {}

		self.all_task_gen = []
		self.task_gen_cache_names = {}
		self.cache_sig_vars = {}
		self.log = None

		self.root = None
		self.srcnode = None
		self.bldnode = None

		# now your head will explode .. :-)
		class node_class(Node.Node):
			pass
		self.node_class = node_class
		self.node_class.__module__ = "Node"
		self.node_class.__name__ = "Nodu"
		self.node_class.bld = self

	def load(self):
		"load the cache from the disk"
		try:
			env = Environment.Environment(os.path.join(self.cachedir, 'build.config.py'))
		except (IOError, OSError):
			pass
		else:
			if env['version'] < HEXVERSION:
				raise Utils.WafError('Version mismatch! reconfigure the project')
			for t in env['tools']:
				self.setup(**t)

		try:
			gc.disable()
			f = data = None

			Node.Nodu = self.node_class

			try:
				f = open(os.path.join(self.bdir, DBFILE), 'rb')
			except (IOError, EOFError):
				# handle missing file/empty file
				pass

			try:
				if f: data = cPickle.load(f)
			except AttributeError:
				# handle file of an old Waf version
				# that has an attribute which no longer exist
				# (e.g. AttributeError: 'module' object has no attribute 'BuildDTO')
				if Logs.verbose > 1: raise

			if data:
				for x in SAVED_ATTRS: setattr(self, x, data[x])
			else:
				debug('build: Build cache loading failed')

		finally:
			if f: f.close()
			gc.enable()

	def save(self):
		"store the cache on disk, see self.load"
		gc.disable()
		self.root.__class__.bld = None

		Node.Nodu = self.node_class
		file = open(os.path.join(self.bdir, DBFILE), 'wb')
		data = {}
		for x in SAVED_ATTRS: data[x] = getattr(self, x)
		cPickle.dump(data, file, -1) # remove the '-1' for unoptimized version
		file.close()
		self.root.__class__.bld = self
		gc.enable()

class FSNode(object):
	__slots__ = ('parent', 'name', 'sig', 'deps')

class FileSystem(object):
	def __init__(self):
		self._nodes = {}

	nodes = property(self._nodes)
	
