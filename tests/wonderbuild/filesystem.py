#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import sys, os, os.path, stat, gc, cPickle
from fnmatch import fnmatchcase as match

from logger import is_debug, debug

class FileSystem(object):
	def __init__(self, project):
		self.project = project
		self.cache_path = os.path.join(project.cache_dir, 'filesystem')
		self.load()
		self.cur = self.root.rel_node(os.getcwd())
		self.cur._kind = DIR

	def load(self):
		gc.disable()
		try:
			try:
				f = file(self.cache_path, 'rb')
				try: self.root = cPickle.load(f)
				finally: f.close()
			except Exception, e:
				print >> sys.stderr, 'could not load pickle:', e
				self.root = Node(None, os.sep)
				self.root._kind = DIR
		finally: gc.enable()

	def dump(self):
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
	
	def display(self):
		print 'fs:'
		self.root.display()

DIR = 1
FILE = 2
ignore = ['.svn']

class Node(object):
	__slots__ = ('parent', 'name', '_kind', '_declared_children', '_old_children', '_actual_children', 'old_time', '_actual_time', '_sig', '_abs_path')

	def __getstate__(self):
		return self.parent, self.name, self._kind, self._old_children, self.old_time, self._sig, self._abs_path

	def __setstate__(self, data):
		self.parent, self.name, self._kind, self._old_children, self.old_time, self._sig, self._abs_path = data
		self._declared_children = None
		self._actual_children = None
		self._actual_time = None

	def __init__(self, parent, name):
		assert parent is not None or name == os.sep
		self.parent = parent
		self.name = name
		self._kind = None
		self._declared_children = None
		self._old_children = None
		self._actual_children = None
		self.old_time = None
		self._actual_time = None
		self._sig = None
		self._abs_path = None
	
	def search_dir_or_file_iter(self, in_pat = '*', ex_pat = None):
		if (ex_pat is None or not match(self.name, ex_pat)) and match(self.name, in_pat): yield self
		if self.is_dir:
			for child in self.actual_children.itervalues():
				for node in child.search_iter(in_pat, ex_pat): yield node
		raise StopIteration
	
	def search_iter(self, in_pat = '*', ex_pat = None):
		for child in self.actual_children.itervalues():
			if (ex_pat is None or not match(child.name, ex_pat)) and match(child.name, in_pat): yield child
			elif child.is_dir:
				for node in child.search_iter(in_pat, ex_pat): yield node
		raise StopIteration

	def do_stat(self):
		global is_debug
		if is_debug: debug('os.stat   : ' + self.abs_path)
		
		# try-except is a tiny bit faster
		#st = os.lstat(self.abs_path)
		#if stat.S_ISLNK(st.st_mode):
			#try: st = os.stat(self.abs_path)
			#except OSError: pass # may be a broken symlink

		try: st = os.stat(self.abs_path)
		except OSError:
			# may be a broken symlink
			st = os.lstat(self.abs_path)

		if stat.S_ISDIR(st.st_mode): self._kind = DIR
		else: self._kind = FILE
		
		self._actual_time = st.st_mtime

	def kind(self):
		if self._kind is None: self.do_stat()
		return self._kind
	kind = property(kind)

	def is_dir(self): return self.kind == DIR
	is_dir = property(is_dir)

	def actual_time(self):
		if self._actual_time is None: self.do_stat()
		return self._actual_time
	actual_time = property(actual_time)

	def changed(self):
		if self.actual_time != self.old_time: return True
		if self.is_dir:
			for n in self.old_children:
				if n.changed(): return True
		return False
		
	def mark_read(self):
		self.old_time = self.actual_time
		if self.is_dir: self._old_children = self.actual_children

	def actual_children(self):
		if self._actual_children is None:
			if self.actual_time == self.old_time: self._actual_children = self.old_children
			else:
				global is_debug
				if is_debug: debug('os.listdir: ' + self.abs_path + os.sep)
				children = {}
				for name in os.listdir(self.abs_path):
					if name in ignore: continue
					if name in self.declared_children: children[name] = self.declared_children[name]
					#if name in self.old_children: children[name] = self.old_children[name]
					else:
						child = Node(self, name)
						children[name] = child
						self.declared_children[name] = child
				self._actual_children = children
		return self._actual_children
	actual_children = property(actual_children)
		
	def old_children(self):
		if self._old_children is None:
			global is_debug
			if is_debug: debug('os.listdir: ' + self.abs_path + os.sep)
			children = {}
			for name in os.listdir(self.abs_path):
				if name in ignore: continue
				#if name in self.declared_children: children[name] = self.declared_children[name]
				#else: children[name] = Node(self, name)
				children[name] = Node(self, name)
			self._old_children = children
		return self._old_children
	old_children = property(old_children)

	def declared_children(self):
		if self._declared_children is None:
			if self._actual_children is not None: self._declared_children = self._actual_children
			elif self._old_children is not None: self._declared_children = self._old_children
			else: self._declared_children = {}
		return self._declared_children
	declared_children = property(declared_children)

	def sig(self):
		if self._sig is None:
			time = self.actual_time
			assert time is not None
			if self._kind == DIR:
				for n in self.actual_children.itervalues():
					sub_time = n.sig
					if sub_time > time: time = sub_time
			self._sig = time
			self.mark_read()
		return self._sig
	sig = property(sig)

	def sig_to_string(self): return str(self.sig)
	
	def find_rel_node(self, path): return self._find_rel_node(path)
	def _findrel_node(self, path, start = 0):
		sep = path.find(os.sep, start)
		if sep > start:
			name = path[start:sep]
			if name == os.pardir: return self.parent or self
			if name == os.curdir: return self
			if self.kind != DIR: return None
			child = self.actual_children.get(name, None)
			if child is None: return None
			if sep == len(path) - 1: return child
			if child.kind != DIR: return None
			sep += 1
			while path[sep] == os.sep: sep += 1
			return child._find_rel_node(path, sep)
		elif sep < 0:
			name = path[start:]
			if name == os.pardir: return self.parent or self
			if name == os.curdir: return self
			if self.kind != DIR: return None
			return self.actual_children.get(name, None)
		else: # sep == start, absolute path
			root = self
			while root.parent: root = root.parent
			assert root.name == os.sep
			return root._find_rel_node(path, 1)

	def rel_node(self, path): return self._rel_node(path)
	def _rel_node(self, path, start = 0):
		sep = path.find(os.sep, start)
		if sep > start:
			name = path[start:sep]
			if name == os.pardir: return self.parent or self
			if name == os.curdir: return self
			child = Node(self, name)
			self.declared_children[name] = child
			if sep == len(path) - 1: return child
			child._kind = DIR
			sep += 1
			while path[sep] == os.sep: sep += 1
			return child._rel_node(path, sep)
		elif sep < 0:
			name = path[start:]
			if name == os.pardir: return self.parent or self
			if name == os.curdir: return self
			child = Node(self, name)
			self.declared_children[name] = child
			return child
		else: # sep == start, absolute path
			root = self
			while root.parent: root = root.parent
			assert root.name == os.sep
			return root._rel_node(path, 1)

	def abs_path(self):
		if self._abs_path is None:
			if not self.parent: abs_path = self.name
			else: abs_path = os.path.join(self.parent.abs_path, self.name)
			self._abs_path = abs_path
		return self._abs_path
	abs_path = property(abs_path)

	def rel_path(self): return self.abs_path
	rel_path = property(rel_path)

	def display(self, cache = False, tabs = 0):
		if True: path = '  |' * tabs + '- ' + (self.parent and self.name or self.abs_path)
		else: path = self.rel_path
		
		if cache: time = self.old_time is None and '?' or self.old_time
		else: time = self._actual_time is None and '?' or self._actual_time
		
		print \
			(self._sig is None and '?' or self._sig).rjust(12), \
			str(time).rjust(12), \
			(self._kind is None and '?' or {DIR: 'dir', FILE: 'file'}[self._kind]).rjust(4) + \
			' ' + path
			
		if cache:
			if self._old_children is not None:
				tabs += 1
				for n in self._old_children.itervalues(): n.display(cache, tabs)
		else:
			if self._declared_children is not None:
				tabs += 1
				for n in self._declared_children.itervalues(): n.display(cache, tabs)
