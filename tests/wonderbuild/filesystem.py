#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import sys, os, os.path, stat, gc, cPickle
from hashlib import md5 as Sig

from signature import raw_to_hexstring

if '--debug' in sys.argv:
	def debug(s): print >> sys.stderr, s
else:
	def debug(s): pass

class FileSystem(object):
	def __init__(self, cache_path = '/tmp/filesystem.cache'):
		self.nodes = {}
		self.cache_path = cache_path
		self.load()

	load_dump_attributes = ('nodes',)

	def load(self):
		gc.disable()
		try:
			try:
				f = file(self.cache_path, 'rb')
				try: data = cPickle.load(f)
				finally: f.close()
				for x in self.load_dump_attributes: setattr(self, x, data[x])
			except Exception, e:
				print >> sys.stderr, 'could not load pickle:', e
				self.nodes = {}
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
	
	def declare(self, name, monitor = False):
		name = os.path.normpath(name)
		try: return self.nodes[name]
		except KeyError:
			n = Node(None, name, monitor = monitor)
			self.nodes[name] = n
			return n

	def changed(self):
		some_changed = None
		for n in self.nodes.itervalues():
			changed = n.changed()
			if changed:
				if some_changed: some_changed += '\n' + changed
				else: some_changed = changed
		return some_changed
	
	def sig(self):
		sig = Sig()
		for n in self.nodes.itervalues():
			if n.monitor: sig.update(n.sig)
		return sig.digest()
	sig = property(sig)

	def sig_to_hexstring(self): return raw_to_hexstring(self.sig)

	def display(self):
		for n in self.nodes.itervalues(): n.display()

UNKNOWN = 0
DIR = 1
FILE = 2

class Node(object):
	__slots__ = ('_abs_path', 'parent', 'name', 'kind', 'children', 'monitor', 'time', '_sig')

	def __init__(self, parent, name, kind = UNKNOWN, monitor = False, time = None):
		self.parent = parent
		self.name = name
		self.kind = kind
		self.children = None
		self.monitor = monitor
		self.time = time
		
	def abs_path(self):
		try: return self._abs_path
		except AttributeError:
			if not self.parent: abs_path = self.name
			else: abs_path = os.path.join(self.parent.abs_path, self.name)
			self._abs_path =  abs_path
			return abs_path
	abs_path = property(abs_path)
	
	def maybe_stat(self):
		if self.time is None: self.do_stat()

	def do_stat(self):
		debug('os.stat   : ' + self.abs_path)
		
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

	def changed(self, parent_path = None):
		if not self.monitor: return None
		old_time = self.time
		if old_time is None: return 'A ' + self.abs_path
		try: self.do_stat()
		except OSError:
			if self.parent:
				del self.parent._sig
				del self.parent.children[self.name]
			del self._sig
			return 'D ' + self.abs_path
		some_changed = None
		if self.time != old_time:
			some_changed = 'U ' + self.abs_path
		if self.kind == DIR:
			self.maybe_list_children()
			if self.time != old_time:
				for name in os.listdir(self.abs_path):
					if not name in self.children: self.children[name] = Node(self, name, monitor = True)
			for n in self.children.values(): # copy because children remove themselves
				changed = n.changed()
				if changed:
					if some_changed: some_changed += '\n' + changed
					else: some_changed = changed
		if some_changed: del self._sig
		return some_changed

	def sig(self):
		try: return self._sig
		except AttributeError:
			if not self.monitor: return ''
			self.maybe_stat()
			assert self.time is not None
			sig = Sig(str(self.time))
			if self.kind == DIR:
				self.maybe_list_children()
				for n in self.children.itervalues(): sig.update(n.sig)
			sig = sig.digest()
			self._sig = sig
			return sig
	sig = property(sig)
	
	def sig_to_hexstring(self): return raw_to_hexstring(self.sig)
	
	def maybe_list_children(self):
		if self.children is None: self.do_list_children()
	
	def do_list_children(self):
		debug('os.listdir: ' + self.abs_path)
		self.children = {}
		for name in os.listdir(self.abs_path): self.children[name] = Node(self, name, monitor = self.monitor)

	def find(self, path, monitor = False):
		r = self._find(path)
		if monitor and r and not r.monitor: r.monitor = True
		return r
	def _find(self, path, start = 0):
		sep = path.find(os.sep, start)
		if sep > start:
			name = path[start:sep]
			if name == os.pardir: return self.parent or self
			if name == os.curdir: return self
			self.maybe_stat()
			if self.kind != DIR: return None
			self.maybe_list_children()
			child = self.children.get(name, None)
			if child is None: return None
			if sep == len(path) - 1: return child
			child.maybe_stat()
			if child.kind != DIR: return None
			return child._find(path, sep + 1)
		elif sep < 0:
			name = path[start:]
			if name == os.pardir: return self.parent or self
			if name == os.curdir: return self
			self.maybe_stat()
			if self.kind != DIR: return None
			self.maybe_list_children()
			return self.children.get(name, None)
		else: # sep == start, absolute path
			top = self
			while top.parent: top = top.parent
			if top.name != os.sep:
				print >> sys.stderr, 'creating root node due to:', path
				root = Node(None, os.sep, DIR, monitor = False)
				top.parent = root.find(os.path.dirname(os.getcwd()))
			else: root = top
			return root._find(path, 1)

	def display(self, tabs = 0):
		if False: path = '  |' * tabs + '- ' + (self.parent and self.name  or self.abs_path)
		else: path = self.abs_path

		if self.monitor: sig = self.sig_to_hexstring()
		else: sig = 'unmonitored'

		print \
			sig, \
			(self.time is None and ' ' or str(self.time)).rjust(12), \
			{UNKNOWN: '', DIR: 'dir', FILE: 'file'}[self.kind].rjust(4) + \
			' ' + path

		if not self.children: return
		tabs += 1
		for n in self.children.itervalues(): n.display(tabs)

if __name__ == '__main__':
	import time
	
	t0 = time.time()
	fs = FileSystem()
	print >> sys.stderr, 'load time:', time.time() - t0
	
	args = [x for x in sys.argv[1:] if not x.startswith('-')]
	if len(args): paths = args
	else: paths = [os.curdir]

	paths = [os.path.abspath(p) for p in paths]
	#top = fs.declare(os.path.commonprefix(paths))
	for n in fs.nodes.values(): # copy because we remove
		if n.abs_path not in paths: del fs.nodes[n.name]
	for p in paths: fs.declare(p, monitor = True)

	#n = fs.declare('waf-test')
	#n = fs.declare('unit_tests')
	
	#t0 = time.time()
	#print >> sys.stderr, 'old sig: ' + fs.sig_to_hexstring()
	#print >> sys.stderr, 'walk time:', time.time() - t0

	t0 = time.time()
	print >> sys.stderr, 'changed:\n' + str(fs.changed())
	print >> sys.stderr, 'sig check time:', time.time() - t0

	t0 = time.time()
	print >> sys.stderr, 'new sig: ' + fs.sig_to_hexstring()
	print >> sys.stderr, 'sig time:', time.time() - t0

	fs.display()
	
	t0 = time.time()
	fs.dump()
	print >> sys.stderr, 'dump time:', time.time() - t0
