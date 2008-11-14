#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os, os.path, stat

class Tree(object):
	def __init__(self):
		self.node_id = 0
		self.nodes = {} # {id: node}
		self.node_abspath = {} # {id: abspath }
		self.dir_lists = {} # {id: [names] }
		self.cache_path = '/tmp/filesystem.cache'

	load_save = ('nodes')

	def load(self):
		gc.disable()
		try:
			try:
				f = file(self.cache_path)
				try: data = cPickle.load(f)
				finally: f.close()
			except:
				self.nodes = {}
			else:
				for x in load_save: setattr(self, x, data[x])
		finally: gc.enable()

	def save(self):
		gc.disable()
		try:
			f = file(self.cache_path)
			try:
				data = {}
				for x in load_save: data[x] = getattr(self, x)
				cPicle.dump(data, f, cPickle.HIGHEST_PROTOCOL)
			finally: f.close()
		finally: gc.enable()
	
	def dump(self):
		for e in self.nodes.itervalues(): e.dump()

UNKNOWN = 0
DIR = 1
FILE = 2

class Entry(object):
	kind = UNKNOWN
	
	__slots__ = ('id', 'parent', 'name', 'time')

	id_counter = 0

	def __init__(self, parent, name, time = None):
		self.id = self.__class__.id_counter
		self.__class__.id_counter += 1
		self.parent = parent
		self.name = name
		self.time = time
		
	def abs_path(self): return not self.parent and self.name or os.path.join(self.parent.abs_path, self.name)
	abs_path = property(abs_path)
	
	def do_stat(self): return os.stat(self.abs_path())
	
	def maybe_stat(self):
		if self.kind != UNKNOWN: return self
		return self.do_stat()

	def do_stat(self):
		st = os.stat(self.abs_path)
		Kind = stat.S_ISDIR(st.st_mode) and Dir or File
		e = Kind(self.parent, self.name, st.st_mtime)
		self.parent.children[self.name] = e
		return e
	
	def dump(self, tabs = 0):
		print \
			str(self.id).rjust(4), \
			(self.time is None and ' ' or str(self.time)).rjust(13), \
			{UNKNOWN: '', DIR: 'dir', FILE: 'file'}[self.kind].ljust(7) + \
			'\t' * tabs, self.parent and self.name  or self.abs_path

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
		return child.find_child(path, sep + 1)
	
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
		st = Entry.do_stat(self)
		if not stat.S_ISDIR(st): raise IOError, 'not a dir'
		return st

	def update_sig(self, sig):
		FSNode.update_sig(self, sig)
		for n in self.children(): n.update_sig(sig)

	def dump(self, tabs = 0):
		Entry.dump(self, tabs)
		if not self.children: return
		tabs += 1
		for e in self.children.itervalues(): e.dump(tabs)

class File(Entry):
	kind = FILE

	def do_stat(self):
		st = Entry.do_stat(self)
		if stat.S_ISDIR(st): raise IOError, 'not a file'
		return st

	def update_sig(self, sig):
		FSNode.update_sig(self, sig)
		stat_sig(sig, self.stat())

if __name__ == '__main__':
	root = Dir(None, os.curdir)
	e = root.find('waf-test').maybe_stat()
	e = root.find('unit_tests').maybe_stat()
	e.maybe_list_stat_children()
	tree = Tree()
	tree.nodes[root.name] = root
	tree.dump()
