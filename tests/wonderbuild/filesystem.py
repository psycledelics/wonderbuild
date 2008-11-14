#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import sys, os, os.path, stat, time, gc, cPickle, signature

class Tree(object):

	id_counter = 0

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
	__slots__ = ('id', 'parent', 'name', 'kind', 'children', 'time', '_sig')

	def __init__(self, parent, name, kind = UNKNOWN, time = None):
		self.id = Tree.id_counter
		Tree.id_counter += 1
		self.parent = parent
		self.name = name
		self.kind = kind
		self.children = None
		self.time = time
		
	def abs_path(self): return not self.parent and self.name or os.path.join(self.parent.abs_path, self.name)
	abs_path = property(abs_path)
	
	def maybe_stat(self):
		if self.time is None: self.do_stat()

	def do_stat(self):
		# try-except is a tiny bit faster
		#st = os.lstat(self.abs_path)
		#if stat.S_ISLNK(st.st_mode): os.stat(self.abs_path)

		try: st = os.stat(self.abs_path)
		except OSError:
			# may be a broken symlink
			st = os.lstat(self.abs_path)

		if stat.S_ISDIR(st.st_mode): self.kind = DIR
		else: self.kind = FILE
		
		self.time = st.st_mtime

	def sig(self):
		try: return self._sig
		except AttributeError:
			self.maybe_stat()
			assert self.time is not None
			sig = signature.Sig(str(self.time))
			if self.kind == DIR:
				self.maybe_list_children()
				for e in self.children.itervalues(): sig.update(e.sig)
			sig = sig.digest()
			self._sig = sig
			return sig
	sig = property(sig)
	
	def sig_to_hexstring(self): return signature.raw_to_hexstring(self.sig)
	
	def changed(self):
		old_time = self.time
		if old_time is None: return self.abs_path + ' (new)'
		try: self.do_stat()
		except OSError:
			if self.parent:
				del self.parent._sig
				del self.parent.children[self.name]
			del self._sig
			return self.abs_path + ' (removed)'
		some_changed = None
		if self.time != old_time:
			some_changed = self.abs_path + ' (time)'
		if self.kind == DIR:
			self.maybe_list_children()
			if self.time != old_time:
				for name in os.listdir(self.abs_path):
					if not name in self.children: self.children[name] = Entry(self, name)
			for e in self.children.values(): # copy because children remove themselves
				changed = e.changed()
				if changed:
					if some_changed: some_changed += '\n' + changed
					else: some_changed = changed
		if some_changed: del self._sig
		return some_changed

	def maybe_list_children(self):
		if self.children is None: self.do_list_children()
	
	def do_list_children(self):
		self.children = {}
		for name in os.listdir(self.abs_path): self.children[name] = Entry(self, name)

	def find(self, path, start = 0):
		sep = path.find(os.sep, start)
		if sep < 0:
			p = path[start:]
			if p == os.pardir: return self.parent or self
			if p == os.curdir: return self
			self.maybe_stat()
			if self.kind != DIR: return None
			self.maybe_list_children()
			return self.children.get(p, None)
		p = path[start:sep]
		if p == os.pardir: return self.parent or self
		if p == os.curdir: return self
		self.maybe_stat()
		if self.kind != DIR: return None
		self.maybe_list_children()
		child = self.children.get(p, None)
		if child is None: return None
		if sep == len(path) - 1: return child
		child.maybe_stat()
		if child.kind == FILE: return None
		return child.find(path, sep + 1)

	def display(self, tabs = 0):
		if False: path = '  |' * tabs + '- ' + (self.parent and self.name  or self.abs_path)
		else: path = self.abs_path
		print \
			str(self.id).rjust(5), \
			signature.raw_to_hexstring(self.sig), \
			(self.time is None and ' ' or str(self.time)).rjust(12), \
			{UNKNOWN: '', DIR: 'dir', FILE: 'file'}[self.kind].rjust(4) + \
			' ' + path
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
		tree.nodes = {}
		root = Entry(None, root_path)
		tree.nodes[root.name] = root
	#e = root.find('waf-test').maybe_stat()
	#e = root.find('unit_tests').maybe_stat()
	#e.maybe_list_stat_children()
	
	t0 = time.time()
	print >> sys.stderr, 'old sig:', root.sig_to_hexstring()
	print >> sys.stderr, 'walk time:', time.time() - t0

	t0 = time.time()
	print >> sys.stderr, 'changed:\n' + str(root.changed())
	print >> sys.stderr, 'sig check time:', time.time() - t0

	t0 = time.time()
	print >> sys.stderr, 'new sig:', root.sig_to_hexstring()
	print >> sys.stderr, 'walk time:', time.time() - t0

	t0 = time.time()
	tree.dump()
	print >> sys.stderr, 'dump time:', time.time() - t0
	
	tree.display()
