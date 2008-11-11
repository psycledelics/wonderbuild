#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

SAVED_ATTRS = 'root srcnode bldnode node_sigs node_deps raw_deps task_sigs id_nodes'.split()
"Build class members to save"

class BuildContext(object):
	"holds the dependency tree"
	def __init__(self):
		# map names to environments, the 'default' must be defined
		self.all_envs = {}

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

	def load(self):
		"load the cache from the disk"
		gc.disable()
		f = open(os.path.join(self.bdir, DBFILE), 'rb')
		data = cPickle.load(f)
		f.close()
		for x in SAVED_ATTRS: setattr(self, x, data[x])
		gc.enable()

	def save(self):
		"store the cache on disk, see self.load"
		gc.disable()
		file = open(os.path.join(self.bdir, DBFILE), 'wb')
		data = {}
		for x in SAVED_ATTRS: data[x] = getattr(self, x)
		cPickle.dump(data, file, -1) # remove the '-1' for unoptimized version
		file.close()
		gc.enable()
