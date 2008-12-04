#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import sys, os, os.path, stat, gc, cPickle
from fnmatch import fnmatchcase as match

from logger import is_debug, debug

class FileSystem(object):
	def __init__(self, cache_path = None):
		self.cache_path = cache_path
		self.load()

	def load(self):
		if self.cache_path is None: self.root = Node(None, os.sep)
		else:
			gc.disable()
			try:
				try: f = file(self.cache_path, 'rb')
				except IOError: raise
				else:
					try: self.root = cPickle.load(f)
					except Exception, e:
						print >> sys.stderr, 'could not load pickle:', e
						raise
					finally: f.close()
			except: self.root = Node(None, os.sep)
			finally: gc.enable()
		self.root._fs = self
		self.root._kind = DIR
		self.root._exists = True
		self.root._height = 0
		if  False and __debug__ and is_debug: self.display(True)
		self.cur = self.root.rel_node(os.getcwd())
		self.cur._fs = self
		self.cur._kind = DIR
		self.cur._exists = True

	def dump(self):
		if self.cache_path is None: return
		gc.disable()
		try:
			f = file(self.cache_path, 'wb')
			try: cPickle.dump(self.root, f, cPickle.HIGHEST_PROTOCOL)
			finally: f.close()
		finally: gc.enable()
		
	def node(self, path):
		return self.cur.rel_node(path)
		
		path = os.path.normpath(path)
		if os.path.isabs(path): return self.root.rel_node(path)
		else: return self.cur.rel_node(path)
	
	def display(self, cache = False):
		print 'fs:', cache and 'cached:' or 'declared:'
		self.root.display(cache)

DIR = 1
FILE = 2
ignore = ['.svn']

if __debug__:
	if is_debug: all_abs_paths = set()

class Node(object):
	__slots__ = (
		'parent', 'name', '_kind', '_children', '_actual_children', '_old_children', '_old_time', '_time', '_sig',
		'_path', '_abs_path', '_height', '_fs', '_exists', '_changed'
	)

	def __getstate__(self):
		if False and __debug__ and is_debug: debug('fs: getstate: ' + self.path + ' ' + str(self._time or self._old_time) + ' ' + str(self._children))
		return self.parent, self.name, self._kind, self._children, self._actual_children or self._old_children, self._time or self._old_time, self._path

	def __setstate__(self, data):
		self.parent, self.name, self._kind, self._children, self._old_children, self._old_time, self._path = data
		self._actual_children = None
		self._time = None
		if False and __debug__ and is_debug: debug('fs: setstate: ' + self.path + ' ' + str(self._old_time) + ' ' + str(self._old_children))

	def __init__(self, parent, name):
		self.parent = parent
		self.name = name
		self._kind = None
		self._children = None
		self._actual_children = None
		self._old_children = None
		self._old_time = None
		self._time = None
		self._path = None
		if __debug__ and is_debug:
			global all_abs_paths
			assert parent is not None or name == os.sep, (parent, name)
			assert parent is None or os.sep not in name, (parent.abs_path, name)
			assert parent is not None or name not in all_abs_paths, (parent, name)
			assert parent is None or os.path.join(parent.abs_path, name) not in all_abs_paths, (parent.abs_path, name)
			debug('fs: new node  : ' + self.abs_path)
			all_abs_paths.add(self.abs_path)
	
	def _do_stat(self):
		if __debug__ and is_debug: debug('fs: os.stat   : ' + self.path)
		try: st = os.stat(self.path)
		except OSError: st = os.lstat(self.path) # may be a broken symlink
		if stat.S_ISDIR(st.st_mode): self._kind = DIR
		else: self._kind = FILE
		self._time = st.st_mtime
		
	@property
	def exists(self):
		try: return self._exists
		except AttributeError:
			if self._time is not None: self._exists = True
			else:
				try: self.parent._did_list_children
				except AttributeError: self._exists = os.path.exists(self.path)
				else: self._exists = self.name in self.parent._children
			return self._exists
	
	def make_dir(self):
		if not self.exists:
			if __debug__ and is_debug: debug('fs: make dir  : ' + self.path)
			os.makedirs(self.path)

	@property
	def kind(self):
		if self._kind is None: self._do_stat()
		return self._kind

	@property
	def is_dir(self): return self.kind == DIR
	
	@property
	def is_file(self): return self.kind == FILE

	@property
	def time(self):
		if self._time is None: self._do_stat()
		return self._time

	@property
	def changed(self):
		try: return self._changed
		except AttributeError:
			if self._old_time is None or self.time != self._old_time:
				self._changed = True
				return True
			if self._kind == DIR:
				for n in self.actual_children.itervalues():
					if n.changed():
						self._changed = True
						return True
			return False

	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			time = self.time
			if self._kind == DIR:
				for n in self.actual_children.itervalues():
					sub_time = n.sig
					if sub_time > time: time = sub_time
			self._sig = time
			return self._sig

	def sig_to_string(self): return str(self.sig)
	
	@property
	def actual_children(self):
		if self._actual_children is None:
			if self.time == self._old_time:
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
				if __debug__ and is_debug: debug('fs: os.listdir: ' + self.path + os.sep)
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
		if __debug__ and is_debug: debug('fs: merge: ' + cur.path + ' ' + old.path)
		if cur._children is None:
			cur._children = old._old_children
			if old._old_time is not None:
				cur._old_time = old._old_time
				cur._kind = old._kind
			elif old._kind is not None: cur._kind = old._kind
			if old._path is not None: cur._path = old._path
		elif old._old_children is None:
			if old._old_time is not None:
				cur._old_time = old._old_time
				cur._kind = old._kind
			elif old._kind is not None: cur._kind = old._kind
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

	def find_iter(self, in_pat = '*', ex_pat = None, prunes = None):
		self.list_children()
		for name, node in self.actual_children.iteritems():
			if (ex_pat is None or not match(name, ex_pat)) and match(name, in_pat): yield node
			elif node.is_dir:
				if prunes is None or name not in prunes:
					for node in node.find_iter(in_pat, ex_pat, prunes): yield node
		raise StopIteration

	#def rel_node(self, *path):
	def rel_node(self, path): return self._rel_node(path)
	def _rel_node(self, path, start = 0):
		sep = path.find(os.sep, start)
		if sep > start:
			name = path[start:sep]
			if name == os.pardir:
				while sep < len(path) - 1 and path[sep] == os.sep: sep += 1
				if sep == len(path) - 1: return self.parent or self
				return (self.parent or self)._rel_node(path, sep)
			if name == os.curdir: return self
			try: child = self.children[name]
			except KeyError:
				child = Node(self, name)
				self.children[name] = child
			child._kind = DIR
			while sep < len(path) - 1 and path[sep] == os.sep: sep += 1
			if sep == len(path) - 1: return child
			return child._rel_node(path, sep)
		elif sep < 0:
			name = path[start:]
			if name == os.pardir: return self.parent or self
			if name == os.curdir: return self
			try: child = self.children[name]
			except KeyError:
				child = Node(self, name)
				self.children[name] = child
			return child
		else: # sep == start, absolute path
			return self.fs.root._rel_node(path, 1)
	
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
		if self._path is None:
			path = []
			cur = self.fs.cur
			node1 = self
			node2 = cur
			node1.height
			node2.height
			while node1._height > node2._height: node1 = node1.parent
			while node1._height < node2._height: node2 = node2.parent
			while node1 is not node2:
				node1 = node1.parent
				node2 = node2.parent
			ancestor = node1
			for i in xrange(cur._height - ancestor._height): path.append(os.pardir)
			down = self._height - ancestor._height
			if down > 0:
				node = self
				path2 = []
				for i in xrange(down):
					path2.append(node.name)
					node = node.parent
				path2.reverse()
				path += path2
			if len(path) == 0: self._path = os.curdir
			else: self._path = os.sep.join(path)
		return self._path

	@property
	def abs_path(self):
		try: return self._abs_path
		except AttributeError:
			if self.parent is None: self._abs_path = self.name
			else: self._abs_path = os.path.join(self.parent.abs_path, self.name)
			return self._abs_path

	def display(self, cache = False, tabs = 0):
		if True: path = '  |' * tabs + '- ' + self.name
		else: path = self.abs_path
		
		if cache: time = self._old_time is None and '?' or self._old_time
		else: time = self._time is None and '?' or self._time
		
		print \
			(str(getattr(self, '_sig', '?'))).rjust(12), \
			str(time).rjust(12), \
			(self._kind is None and '?' or {DIR: 'dir', FILE: 'file'}[self._kind]).rjust(4) + \
			' ' + path
			
		if cache:
			if self._actual_children is not None:
				tabs += 1
				for n in self._actual_children.itervalues(): n.display(cache, tabs)
			elif self._old_children is not None:
				tabs += 1
				for n in self._old_children.itervalues(): n.display(cache, tabs)
		else:
			if self._children is not None:
				tabs += 1
				for n in self._children.itervalues():
					if self._actual_children is not None and not n.name in self._actual_children: continue
					if self._old_children is not None and not n.name in self._old_children: continue
					n.display(cache, tabs)
