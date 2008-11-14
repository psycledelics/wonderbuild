#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import sys, os, os.path, stat, time, gc, cPickle, signature

class Tree(object):
	def __init__(self):
		self.node_id = 0
		self.nodes = {} # {id: node}
		self.node_abspath = {} # {id: abspath }
		self.dir_lists = {} # {id: [names] }
		self.cache_path = '/tmp/filesystem.cache'

	load_dump_attributes = ('nodes',)

	def load(self):
		gc.disable()
		try:
			try:
				f = file(self.cache_path, 'rb')
				try: data = cPickle.load(f)
				finally: f.close()
			except Exception, e:
				print >> sys.stderr, 'could not load pickle:', e
				self.nodes = {}
			else:
				for x in self.load_dump_attributes: setattr(self, x, data[x])
		finally: gc.enable()

	def dump(self):
		gc.disable()
		try:
			f = file(self.cache_path, 'wb')
			try:
				data = {}
				for x in self.load_dump_attributes: data[x] = getattr(self, x)
				cPickle.dump(data, f, cPickle.HIGHEST_PROTOCOL)
			finally: f.close()
		finally: gc.enable()
	
	def display(self):
		for e in self.nodes.itervalues(): e.display()

UNKNOWN = 0
DIR = 1
FILE = 2

class Entry(object):
	kind = UNKNOWN
	
	__slots__ = ('id', 'parent', 'name', 'time', '_sig')

	id_counter = 0

	def __init__(self, parent, name, time = None):
		self.id = self.id_counter
		self.__class__.id_counter += 1
		self.parent = parent
		self.name = name
		self.time = time
		
	def abs_path(self): return not self.parent and self.name or os.path.join(self.parent.abs_path, self.name)
	abs_path = property(abs_path)
	
	def maybe_stat(self):
		if self.time is None: return self.do_stat()
		return self

	def do_stat(self):
		try: st = os.stat(self.abs_path)
		except OSError:
			# may be a broken symlink
			st = os.lstat(self.abs_path)
		Kind = stat.S_ISDIR(st.st_mode) and Dir or File
		e = Kind(self.parent, self.name, st.st_mtime)
		if self.parent: self.parent.children[self.name] = e
		assert e.kind != UNKNOWN
		assert e.time is not None
		return e

	def get_sig(self):
		try: return self._sig
		except AttributeError:
			time = self.maybe_stat().time
			assert time is not None
			self._sig = signature.Sig(str(time)).hexdigest()
			return self._sig
	sig = property(get_sig)
		
	def update_sig(self, sig):
		time = self.maybe_stat().time
		assert time is not None
		sig.update(str(time))

	def display(self, tabs = 0):
		if False: sig = ''
		else: sig = self.sig
		
		return
		
		if False: path = '  |' * tabs + '- ' + (self.parent and self.name  or self.abs_path)
		else: path = self.abs_path
		
		print \
				str(self.id).rjust(5), \
				sig, \
				(self.time is None and ' ' or str(self.time)).rjust(12), \
				{UNKNOWN: '', DIR: 'dir', FILE: 'file'}[self.kind].ljust(5) + \
				path

class File(Entry):
	kind = FILE

	def do_stat(self):
		e = Entry.do_stat(self)
		if e.kind != FILE: raise IOError, 'not a file: ' + self.abs_path
		return e

class Dir(Entry):
	kind = DIR
	
	__slots__ = ('children')

	def __init__(self, parent, name, time = None):
		Entry.__init__(self, parent, name, time)
		self.children = None
	
	def find(self, path, start = 0):
		sep = path.find(os.sep, start)
		if sep < 0:
			p = path[start:]
			if p == os.pardir: return self.parent or self
			if p == os.curdir: return self
			self.maybe_list_children()
			return self.children.get(p, None)
		p = path[start:sep]
		if p == os.pardir: return self.parent or self
		if p == os.curdir: return self
		self.maybe_list_children()
		child = self.children.get(p, None)
		if child is None: return None
		if sep == len(path) - 1: return child
		child = child.maybe_stat()
		if child.kind == FILE: return None
		return child.find(path, sep + 1)
	
	def maybe_list_children(self):
		if self.children is None: self.do_list_children()
	
	def do_list_children(self):
		path = self.abs_path
		self.children = {}
		for name in os.listdir(path): self.children[name] = Entry(self, name)

	def maybe_list_stat_children(self):
		self.maybe_list_children()
		for e in self.children.itervalues(): e.maybe_stat()
	
	def do_list_stat_children(self):
		path = self.abs_path
		self.children = {}
		for name in os.listdir(path):
			st = os.stat(os.path.join(path, name))
			Kind = stat.S_ISDIR(st.st_mode) and Dir or Kind
			self.children[name] = Kind(self, name, st.st_mtime)

	def do_stat(self):
		e = Entry.do_stat(self)
		if e.kind != DIR: raise IOError, 'not a dir: ' + self.abs_path
		return e

	def get_sig(self):
		sig = signature.Sig(Entry.get_sig(self))
		self.maybe_list_stat_children()
		for e in self.children.itervalues(): e.update_sig(sig)
		return sig.hexdigest()
	sig = property(get_sig)

	def update_sig(self, sig):
		Entry.update_sig(self, sig)
		self.maybe_list_stat_children()
		for e in self.children.itervalues(): e.update_sig(sig)

	def display(self, tabs = 0):
		Entry.display(self, tabs)
		if not self.children: return
		tabs += 1
		for e in self.children.itervalues(): e.display(tabs)

if __name__ == '__main__':
	tree = Tree()
	t0 = time.time()
	tree.load()
	print >> sys.stderr, 'load time:', time.time() - t0
	
	root_path = sys.argv[1] or os.curdir
	root = tree.nodes.get(root_path, None)
	if not root:
		root = Dir(None, root_path)
		tree.nodes[root.name] = root
	#e = root.find('waf-test').maybe_stat()
	#e = root.find('unit_tests').maybe_stat()
	#e.maybe_list_stat_children()
	
	t0 = time.time()
	tree.display()
	print >> sys.stderr, 'walk time:', time.time() -t0

	t0 = time.time()
	tree.dump()
	print >> sys.stderr, 'dump time:', time.time() -t0
	
