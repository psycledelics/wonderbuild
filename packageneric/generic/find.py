# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006 johan boule <bohan@jabber.org>
# copyright 2006 psycledelics http://psycle.pastnotecut.org

import os, fnmatch

class find:
	'''a forward iterator that traverses a directory tree'''
	
	def __init__(
		self,
		packageneric,
		strip_path,
		path,
		pattern = '*'
	):
		self._packageneric = packageneric
		self._strip_path = strip_path
		self._stack = [path]
		self._pattern = pattern
		self._files = []
		self._index = 0
		
	def packageneric(self):
		return self._packageneric
		
	def strip_path(self):
		return self._strip_path
	
	def __getitem__(self, index):
		while True:
			try:
				file = self._files[self._index]
				self._index += 1
			except IndexError:
				# pop next directory from stack
				self._directory = self._stack.pop()
				self._files = os.listdir(os.path.join(self.strip_path(), self._directory))
				self._index = 0
			else:
				# got a filename
				path = os.path.join(self._directory, file)
				if os.path.isdir(os.path.join(self.strip_path(), path)):
					self._stack.append(path)
				if fnmatch.fnmatchcase(file, self._pattern):
					return path

def print_all_nodes(dirnode, level = 0):
	'''prints all the scons nodes that are children of this node, recursively.'''
	if type(dirnode)==type(''):
		dirnode=Dir(dirnode)
	dt = type(Dir('.'))
	for f in dirnode.all_children():
		if type(f) == dt:
			print "%s%s: .............." % (level * ' ', str(f))
			print_dir(f, level+2)
		print "%s%s" % (level * ' ', str(f))

def glob(includes = ['*'], excludes = None, dir = '.'):
	'''similar to glob.glob, except globs SCons nodes, and thus sees generated files and files from build directories.
	Basically, it sees anything SCons knows about.
	A key subtlety is that since this function operates on generated nodes as well as source nodes on the filesystem,
	it needs to be called after builders that generate files you want to include.
	
	It will return both Dir entries and File entries
	'''
	
	def fn_filter(node):
		fn = os.path.basename(str(node))
		match = False
		for include in includes:
			if fnmatch.fnmatchcase(fn, include):
				match = True
				break
		if match and not excludes is None:
			for exclude in excludes:
				if fnmatch.fnmatchcase(fn, exclude):
					match = False
					break
		return match

	def filter_nodes(where):
		children = filter(fn_filter, where.all_children(scan = False))
		nodes = []
		for f in children:
			nodes.append(gen_node(f))
		return nodes

	def gen_node(n):
		'''Checks first to see if the node is a file or a dir, then creates the appropriate node.
		(code seems redundant, if the node is a node, then shouldn't it just be left as is?)
		'''
		if type(n) in (type(''), type(u'')):
			path = n
		else:
			path = n.abspath
		if os.path.isdir(path):
			return Dir(n)
		else:
			return File(n)
	
	here = Dir(dir)
	nodes = filter_nodes(here)
	node_srcs = [n.srcnode() for n in nodes]
	src = here.srcnode()
	if src is not here:
		for s in filter_nodes(src):
			if s not in node_srcs:
				# Probably need to check if this node is a directory
				nodes.append(gen_node(os.path.join(dir, os.path.basename(str(s)))))
	return nodes
