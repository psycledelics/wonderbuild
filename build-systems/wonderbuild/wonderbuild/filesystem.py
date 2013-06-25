#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2011 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import sys, os, errno, stat, threading
from collections import deque
from fnmatch import fnmatchcase as match

from logger import is_debug, debug

# define to True to use hash sum (e.g. md5 sum) instead of timestamps for signatures
USE_HASH_SUM = False
if USE_HASH_SUM: from signature import Sig

class FileSystem(object):
	def __init__(self, persistent):
		cwd = os.getcwd()
		try: self.root = persistent[str(self.__class__)]
		except KeyError:
			if  __debug__ and is_debug: debug('fs: all anew')
			self.root = Node(None, os.sep)
			persistent[str(self.__class__)] = self.root
		self.root._fs = self
		self.root._exists = self.root._is_dir = True
		self.root._is_symlink = False
		self.root._canonical_node = self.root
		self.root._height = 0
		self.cur = self.root / cwd
		self.cur._fs = self
		self.cur._exists = self.cur._is_dir = True
		
	def purge(self, global_purge):
		if global_purge: self.root._global_purge_unused_children()
		else: self.root._partial_purge_unused_children()
		if __debug__ and is_debug: debug('fs: purged     : ' + (global_purge and 'global' or 'partial'))

ignore_names = set(['.git', '.bzr', '.hg', '_MTN', '_darcs', '.svn'])
if False: # old stuff not widely used anymore, so it's not enabled by default
	ignore_names.add('{arch}')
	ignore_names.add('.arch-ids')
	ignore_names.add('CVS')
	ignore_names.add('RCS')
	ignore_names.add('SCCS')
ignore_pats = set(('*~', '#*#'))

def ignore(name):
	return name in ignore_names or \
	any(match(name, ignore_pat) for ignore_pat in ignore_pats)

if __debug__ and is_debug: all_abs_paths = set()

class Node(object):
	__slots__ = (
		'parent', 'name', '_is_dir', '_is_symlink', '_canonical_node', '_children', '_actual_children', '_old_children', '_old_time', '_time', '_sig',
		'_used', '_old_used', '_path', '_abs_path', '_height', '_fs', '_exists', '_lock'
	)

	def __getstate__(self):
		if self._is_dir:
			return self.parent, self.name, self._used or self._old_used, \
				self._children, self._actual_children or self._old_children, self._time or self._old_time
		else:
			return self.parent, self.name, self._used or self._old_used

	def __setstate__(self, data):
		self._is_dir = len(data) != 3
		if self._is_dir:
			self.parent, self.name, self._old_used, \
			self._children, self._old_children, self._old_time = data
		else:
			self.parent, self.name, self._old_used = data
			self._children = self._old_children = self._old_time = None
		self._actual_children = self._time = None
		self._used = False

	def __init__(self, parent, name):
		self.parent = parent
		self.name = name
		self._is_dir = self._children = self._actual_children = self._old_children = self._time = self._old_time = None
		self._used = self._old_used = False
		if __debug__ and is_debug:
			global all_abs_paths
			assert parent is not None or name == os.sep, (parent, name)
			assert parent is None or os.sep not in name, (parent.abs_path, name)
			assert parent is not None or name not in all_abs_paths, (parent, name)
			assert parent is None or os.path.join(parent.abs_path, name) not in all_abs_paths, (parent.abs_path, name)
			debug('fs: new node   : ' + self.abs_path)
			all_abs_paths.add(self.abs_path)
		# no need: if parent is not None: parent.children[name] = self
	
	def _do_stat(self):
		if __debug__ and is_debug:
			debug('fs: os.lstat   : ' + self.abs_path)
		st = os.lstat(self.abs_path)
		self._is_symlink = stat.S_ISLNK(st.st_mode)
		if self._is_symlink:
			if __debug__ and is_debug: debug('fs: os.stat    : ' + self.abs_path)
			try: st = os.stat(self.abs_path)
			except OSError, e:
				if e.errno != errno.ENOENT: raise
				# broken symlink
		self._is_dir = stat.S_ISDIR(st.st_mode)
		self._time = st.st_ctime # note: unlike mtime, ctime is updated when a change in perm or ownership occurs.

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
			if self._time is not None:
				self._exists = True
				return self._exists
			elif self.parent._actual_children is not None:
				self._exists = self.name in self.parent._actual_children
				return self._exists
			elif self.parent._old_children is not None:
				if not self.parent.exists:
					self._exists = False
					return self._exists
				elif self.parent.time == self.parent._old_time:
					self._exists = self.name in self.parent._old_children
					return self._exists
			try: self._do_stat()
			except OSError, e:
				if e.errno != errno.ENOENT: raise
				self._exists = False
			else: self._exists = True
			return self._exists
	
	def make_dir(self, parent_node_to_lock=None):
		if parent_node_to_lock is None:
			if not self.exists:
				if __debug__ and is_debug: debug('fs: os.makedirs: ' + str(self) + os.sep)
				os.makedirs(self.abs_path)
				# why not: self._actual_children = {}; self._used = True
		else:
			lock = parent_node_to_lock.lock
			lock.acquire()
			try:
				if not self.exists:
					if __debug__ and is_debug: debug('fs: os.makedirs: ' + str(self) + os.sep + ' (locking: ' + str(parent_node_to_lock) + os.sep + ')')
					os.makedirs(self.abs_path)
					# why not: self._actual_children = {}; self._used = True
			finally: lock.release()
		self._exists = self._is_dir = True
		self._is_symlink = False

	@property
	def is_dir(self):
		if self._is_dir is None: self._do_stat()
		return self._is_dir
	
	@property
	def is_symlink(self):
		try: return self._is_symlink
		except AttributeError:
			self._do_stat()
			return self._is_symlink

	@property
	def time(self):
		if self._time is None: self._do_stat()
		return self._time

	if not USE_HASH_SUM: # use timestamp sig
		@property
		def sig(self):
			try: return self._sig
			except AttributeError:
				if __debug__ and is_debug: debug('fs: sig        : ' + str(self))
				self._used = True
				if self.is_dir:
					sigs = [n.sig for n in self.actual_children.itervalues()]
					sigs.sort()
					sig = self._sig = Sig(''.join(sigs)).digest()
				else:
					sig = self._sig = str(self.time)
				return sig
	else: # use hash sum sig
		@property
		def sig(self):
			try: return self._sig
			except AttributeError:
				if __debug__ and is_debug: debug('fs: sig        : ' + str(self))
				self._used = True
				if self.is_dir:
					sigs = [n.sig for n in self.actual_children.itervalues()]
					sigs.sort()
					sig = Sig(''.join(sigs))
				else:
					f = open(self.path, 'rb')
					try: sig = Sig(f.read())
					finally: f.close()
				sig = self._sig = sig.digest()
				return sig
	
	@property
	def actual_children(self):
		if self._actual_children is None:
			self._used = True
			if self.time == self._old_time and self._old_children is not None:
				self._actual_children = self._old_children
				self._old_children = None
				if self._children is None:
					self._children = {}
					self._children.update(self._actual_children)
				else:
					for name, node in self._actual_children.iteritems():
						try: child = self._children[name]
						except KeyError: self._children[name] = node
						else: self._merge(child, node)
			else:
				self._actual_children = {}
				if __debug__ and is_debug: debug('fs: os.listdir : ' + str(self) + os.sep)
				if self._children is None:
					self._children = {}
					for name in os.listdir(self.path):
						if not ignore(name): self._children[name] = self._actual_children[name] = Node(self, name)
				else:
					for name in os.listdir(self.path):
						if not ignore(name):
							try: child = self._children[name]
							except KeyError: self._children[name] = self._actual_children[name] = Node(self, name)
							else: self._actual_children[name] = child
		return self._actual_children
	
	def _merge(self, cur, old):
		if __debug__ and is_debug:
			debug('fs: merge      : ' + str(cur))
			assert cur.path == old.path
		if cur._children is None:
			cur._children = old._old_children
			if old._old_time is not None:
				cur._old_time = old._old_time
				cur._is_dir = old._is_dir
			elif old._is_dir is not None: cur._is_dir = old._is_dir
		elif old._old_children is None:
			if old._old_time is not None:
				cur._old_time = old._old_time
				cur._is_dir = old._is_dir
			elif old._is_dir is not None: cur._is_dir = old._is_dir
		else:
			for name, node in old._old_children.iteritems():
				try: child = cur._children[name]
				except KeyError: cur._children[name] = node
				else: self._merge(child, node)
	
	@property
	def children(self):
		if self._children is None:
			self._children = {}
			if self._actual_children is not None: self._children.update(self._actual_children)
			elif self._old_children is not None: self._children.update(self._old_children)
		return self._children

	def find_iter(self, in_pats=('*',), ex_pats=None, prune_pats=None):
		if __debug__ and is_debug: debug('fs: find_iter  : ' + str(self) + os.sep + ' ' + str(in_pats) + ' ' + str(ex_pats) + ' ' + str(prune_pats))
		for name, node in self.actual_children.iteritems():
			matched = False
			if ex_pats is not None:
				for pat in ex_pats:
					if match(name, pat): matched = True; break
			if not matched:
				for pat in in_pats:
					if match(name, pat): matched = True; yield node; break
				if not matched and node.is_dir:
					if prune_pats is not None:
						for pat in prune_pats:
							if match(name, pat): matched = True; break
					if not matched:
						for node in node.find_iter(in_pats, ex_pats, prune_pats): yield node
	
	def __div__(self, path): return self.__truediv__(path) # truediv has become the default div in python 3.0 (that's //, not / !)

	def __truediv__(self, path):
		if os.path.isabs(path) and self is not self.fs.root: return self.fs.root / path
		node = self
		for name in path.split(os.sep):
			if len(name) == 0: continue
			if name == os.pardir: node = node.parent or node # note: 'dir/symlink/..' becomes 'dir/', which changes the meaning of the path (just like os.path.normpath does)
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

	def __str__(self): return self.path
	
	@property
	def path(self):
		try: return self._path
		except AttributeError:
			self._path = self.rel_path(self.fs.cur.canonical_node)
			return self._path

	@property
	def canonical_node(self):
		try: return self._canonical_node
		except AttributeError:
			if __debug__ and is_debug: debug('fs: os.path.realpath: ' + self.abs_path)
			path = os.path.realpath(self.abs_path)
			self.fs.root.lock.acquire()
			try:
				self._canonical_node = self.fs.root / path
				self._canonical_node._abs_path = path
			finally: self.fs.root.lock.release()
			return self._canonical_node
	
	def rel_path(self, from_node, allow_abs_path=True):
		if from_node.exists:
			if from_node.is_symlink: from_node = from_node.canonical_node # because 'dir/symlink/..' is not the same as 'dir/'
			if not from_node.is_dir: from_node = from_node.parent
		node1 = from_node
		node2 = self
		node1.height
		node2.height
		# TODO minor optim: A small optimisation could be done for the 'dir/symlink/..' case in the loop, indeed
		# TODO minor optim: once we've canonicalised the node there is no need to check for symlinks anymore.
		while node1._height > node2._height:
			if node1.exists and node1.is_symlink: return self.rel_path(from_node.canonical_node) # because 'dir/symlink/..' is not the same as 'dir/'
			node1 = node1.parent
		while node1._height < node2._height:
			node2 = node2.parent
		while node1 is not node2:
			if node1.exists and node1.is_symlink: return self.rel_path(from_node.canonical_node) # because 'dir/symlink/..' is not the same as 'dir/'
			node1 = node1.parent
			node2 = node2.parent
		ancestor = node1
		if ancestor._height == 0 and allow_abs_path:
			# Relative paths are useful to be able to move a common ancestor while keeping these relative paths between children valid.
			# If we need to go up to the root, it's useless to use a relative path because the root itself never moves.
			# We use the absolute path which is simpler for the user to read.
			# There is one, far fetched, case where disabling this proved useful: in generate_pkg_config_file; see there for the gory details.
			return self.abs_path
		path = []
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

	def clear(self):
		if __debug__ and is_debug: debug('fs: clear      : ' + str(self))
		self._time = None
		try: del self._sig
		except AttributeError: pass
		try: del self._exists
		except AttributeError: pass
		try: del self._is_symlink
		except AttributeError: pass
		try: del self._canonical_node
		except AttributeError: pass
		if self._actual_children is not None: self._actual_children = self._old_children = None
		self._used = False

	def forget(self):
		"detach the node from its parent. This is used to cut from the tree the branches we don't want to dump in the pickle"
		if __debug__ and is_debug: debug('fs: forget     : ' + str(self))
		name = self.name
		parent = self.parent
		if parent._children is not None and name in parent._children: del parent._children[name]
		if parent._actual_children is not None and name in parent._actual_children: del parent._actual_children[name]
		if parent._old_children is not None and name in parent._old_children: del parent._old_children[name]

	if False: # TODO See note in PurgeablePersistentDict
		def _global_purge_unused_children(self):
			c = {}; used = False
			for node in self._children.itervalues():
				if node._used or node._children is not None and not node._global_purge_unused_children():
					c[node.name] = node
					used = True
			self._children = used and c or None
			if not used:
				self._actual_children = self._old_children = None
				if __debug__ and is_debug: debug('fs: unused     : ' + str(self))
			return not used

	def _partial_purge_unused_children(self):
		c = {}; used = False
		for node in self._children.itervalues():
			if node._used or node._old_used or node._children is not None and not node._partial_purge_unused_children():
				c[node.name] = node
				used = True
		self._children = used and c or None
		if not used:
			self._actual_children = self._old_children = None
			if __debug__ and is_debug: debug('fs: unused     : ' + str(self))
		return not used

