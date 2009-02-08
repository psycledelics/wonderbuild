#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import sys, os, stat, threading
from collections import deque
from fnmatch import fnmatchcase as match

from logger import is_debug, debug

class FileSystem(object):
	def __init__(self, state_and_cache):
		try: self.root = state_and_cache[self.__class__.__name__]
		except KeyError:
			if  __debug__ and is_debug: debug('fs: all anew')
			self.root = state_and_cache[self.__class__.__name__] = Node(None, os.sep)
			self.root._is_dir = True
		self.root._exists = True
		self.root._height = 0
		self.root._fs = self
		self.cur = self.root.node_path(os.getcwd())
		self.cur._fs = self
		self.cur._is_dir = True
		self.cur._exists = True
	
ignore = set(['.svn'])

if __debug__ and is_debug: all_abs_paths = set()

class Node(object):
	__slots__ = (
		'parent', 'name', '_is_dir', '_children', '_actual_children', '_old_children', '_old_time', '_time', '_sig',
		'_path', '_abs_path', '_height', '_fs', '_exists', '_lock'
	)

	def __getstate__(self):
		if self._is_dir:
			return self.parent, self.name, self._path, \
				self._children, self._actual_children or self._old_children, self._time or self._old_time
		else:
			return self.parent, self.name, self._path

	def __setstate__(self, data):
		self._is_dir = len(data) != 3
		if self._is_dir:
			self.parent, self.name, self._path, self._children, self._old_children, self._old_time = data
			self._actual_children = self._time = None
		else:
			self.parent, self.name, self._path = data
			self._actual_children = self._time = self._children = self._old_children = self._old_time = None

	def __init__(self, parent, name):
		self.parent = parent
		self.name = name
		self._path = self._is_dir = self._children = self._actual_children = self._old_children = self._time = self._old_time = None
		if __debug__ and is_debug:
			global all_abs_paths
			assert parent is not None or name == os.sep, (parent, name)
			assert parent is None or os.sep not in name, (parent.abs_path, name)
			assert parent is not None or name not in all_abs_paths, (parent, name)
			assert parent is None or os.path.join(parent.abs_path, name) not in all_abs_paths, (parent.abs_path, name)
			debug('fs: new node: ' + self.abs_path)
			all_abs_paths.add(self.abs_path)
		# no need: if parent is not None: parent.children[name] = self
	
	def __str__(self): return self.path
	
	def _do_stat(self):
		if __debug__ and is_debug: debug('fs: os.stat    : ' + self.path)
		try: st = os.stat(self.path)
		except OSError: st = os.lstat(self.path) # may be a broken symlink
		self._is_dir = stat.S_ISDIR(st.st_mode)
		self._time = st.st_mtime

	@property
	def lock(self):
		try: return self._lock
		except AttributeError:
			self._lock = threading.Lock()
			return self._lock
		
	@property
	def exists(self):
		try: return self._exists
		except AttributeError:
			if self._time is not None: self._exists = True
			elif self.parent._actual_children is not None: self._exists = self.name in self.parent._actual_children
			else:
				try: self._do_stat()
				except OSError: self._exists = False
				else: self._exists = True
			return self._exists
	
	def make_dir(self, parent_node_to_lock = None):
		if __debug__ and is_debug: debug('fs: os.makedirs: ' + self.path + os.sep)
		if parent_node_to_lock is None:
			if not self.exists: os.makedirs(self.path)
		else:
			lock = parent_node_to_lock.lock
			lock.acquire()
			try:
				if not self.exists: os.makedirs(self.path)
			finally: lock.release()
		self._exists = self._is_dir = True

	@property
	def is_dir(self):
		if self._is_dir is None: self._do_stat()
		return self._is_dir
	
	@property
	def time(self):
		if self._time is None: self._do_stat()
		return self._time

	def _deep_time(self):
		time = self.time
		if self._is_dir:
			for n in self.actual_children.itervalues():
				sub_time = n._deep_time()
				if sub_time > time: time = sub_time
		return time

	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			if __debug__ and is_debug: debug('fs: sig        : ' + self.path)
			sig = self._sig = str(self._deep_time())
			return sig

	@property
	def actual_children(self):
		if self._actual_children is None:
			if self.time == self._old_time and self._old_children is not None:
				self._actual_children = self._old_children
				self._old_children = None
				if self._children is None:
					self._children = {}
					self._children.update(self._actual_children)
				else:
					for name, node in self._actual_children.iteritems():
						if name in self._children: self._merge(self._children[name], node)
						else: self._children[name] = node
			else:
				self._actual_children = {}
				if __debug__ and is_debug: debug('fs: os.listdir : ' + self.path + os.sep)
				if self._children is None:
					self._children = {}
					for name in os.listdir(self.path):
						if name not in ignore: self._children[name] = self._actual_children[name] = Node(self, name)
				else:
					for name in os.listdir(self.path):
						if name not in ignore:
							if name in self._children: self._actual_children[name] = self._children[name]
							else: self._children[name] = self._actual_children[name] = Node(self, name)
		return self._actual_children
	
	def _merge(self, cur, old):
		if __debug__ and is_debug:
			debug('fs: merge      : ' + cur.path)
			assert cur.path == old.path
		if cur._children is None:
			cur._children = old._old_children
			if old._old_time is not None:
				cur._old_time = old._old_time
				cur._is_dir = old._is_dir
			elif old._is_dir is not None: cur._is_dir = old._is_dir
			if old._path is not None: cur._path = old._path
		elif old._old_children is None:
			if old._old_time is not None:
				cur._old_time = old._old_time
				cur._is_dir = old._is_dir
			elif old._is_dir is not None: cur._is_dir = old._is_dir
			if old._path is not None: cur._path = old._path
		else:
			for name, node in old._old_children.iteritems():
				if name in cur._children: self._merge(cur._children[name], node)
				else: cur._children[name] = node
	
	@property
	def children(self):
		if self._children is None:
			self._children = {}
			if self._actual_children is not None: self._children.update(self._actual_children)
			elif self._old_children is not None: self._children.update(self._old_children)
		return self._children

	def find_iter(self, in_pats = ['*'], ex_pats = None, prune_pats = None):
		if __debug__ and is_debug: debug('fs: find_iter  : ' + self.path + os.sep + ' ' + str(in_pats) + ' ' + str(ex_pats) + ' ' + str(prune_pats))
		for name, node in self.actual_children.iteritems():
			matched = False
			if ex_pats is not None:
				for pat in ex_pats:
					if match(name, pat): matched = True; break
			if not matched:
				for pat in in_pats:
					if match(name, pat): yield node; matched = True; break
				if not matched and node.is_dir:
					if prune_pats is not None:
						for pat in prune_pats:
							if match(name, pat): matched = True; break
					if not matched:
						for node in node.find_iter(in_pats, ex_pats, prune_pats): yield node
		raise StopIteration

	def node_path(self, path):
		if os.path.isabs(path) and self is not self.fs.root: return self.fs.root.node_path(path)
		node = self
		for name in path.split(os.sep):
			if len(name) == 0: continue
			if name == os.pardir: node = node.parent or node
			elif name != os.curdir:
				try: node = node.children[name]
				except KeyError:
					node._is_dir = True
					node.children[name] = node = Node(node, name)
		return node

	@property
	def fs(self):
		try: return self._fs
		except AttributeError:
			fs = self._fs = self.parent.fs
			self._height = self.parent.height + 1
			return fs

	@property
	def height(self):
		try: return self._height
		except AttributeError:
			self.fs
			self._height = self.parent.height + 1
			return self._height

	@property
	def path(self):
		if self._path is None: self._path = self.rel_path(self.fs.cur)
		return self._path

	def rel_path(self, from_node):
		path = []
		node1 = self
		node2 = from_node
		node1.height
		node2.height
		while node1._height > node2._height: node1 = node1.parent
		while node1._height < node2._height: node2 = node2.parent
		while node1 is not node2:
			node1 = node1.parent
			node2 = node2.parent
		ancestor = node1
		for i in xrange(from_node._height - ancestor._height): path.append(os.pardir)
		down = self._height - ancestor._height
		if down > 0:
			node = self
			path2 = deque()
			for i in xrange(down):
				path2.appendleft(node.name)
				node = node.parent
			path += path2
		if len(path) == 0: return os.curdir
		else: return os.sep.join(path)

	@property
	def abs_path(self):
		try: return self._abs_path
		except AttributeError:
			if self.parent is None: self._abs_path = self.name
			else: self._abs_path = os.path.join(self.parent.abs_path, self.name)
			return self._abs_path

	def forget(self):
		"detach the node from its parent. This is used to cut from the tree the branches we don't want to dump in the pickle"
		name = self.name
		parent = self.parent
		if parent._children is not None and name in parent._children: del parent._children[name]
		if parent._actual_children is not None and name in parent._actual_children: del parent._actual_children[name]
		if parent._old_children is not None and name in parent._old_children: del parent._old_children[name]
