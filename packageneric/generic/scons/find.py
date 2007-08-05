# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

import os, fnmatch

class find:
	'a forward iterator that traverses a directory tree'	
	def __init__(
		self,
		project,
		strip_path,
		include_patterns = None,
		exclude_patterns = None
	):
		import packageneric.generic.scons.project
		assert isinstance(project, packageneric.generic.scons.project.project)
		self._project = project
		self._strip_path = strip_path
		if include_patterns is None: self._include_patterns = ['*']
		else:
			assert type(include_patterns) == type([])
			self._include_patterns = include_patterns
		dir_dict = {}
		for include_pattern in self._include_patterns:
			head = self._split_wilcards(include_pattern)
			if not os.path.isdir(os.path.join(self._strip_path, head)): head, tail = os.path.split(head)
			if not len(head): head = '.'
			try: dir_dict[head].append(include_pattern)
			except KeyError: dir_dict[head] = [include_pattern]
		self._stack = []
		for dir, include_patterns in dir_dict.items(): self._stack.append(self._stack_element(dir, include_patterns))
		# Note that the stack may contain foo and foo/bar, and in this case we list the foo/bar dir twice!
		# This is why we have per-dir include patterns so that files aren't found multiple times.
		# todo: This could be optimised by finding common dirs and then only listing the same dir once.
		if exclude_patterns is None: self._exclude_patterns = [os.path.join('*', '.*'), os.path.join('*', 'todo', '*')]
		else:
			assert type(exclude_patterns) == type([])
			self._exclude_patterns = exclude_patterns
		self._files = []
		self._index = 0
		
	def project(self): return self._project
		
	def full_path(self): return os.path.join(self._strip_path, self._relative_path)
	def strip_path(self): return self._strip_path
	def relative_path(self): return self._relative_path

	def __getitem__(self, index):
		while True:
			try:
				file = self._files[self._index]
				self._index += 1
			except IndexError:
				# pop next directory from stack
				stack_element = self._stack.pop()
				self._dir = stack_element._dir
				self._files = []
				for file in os.listdir(os.path.join(self._strip_path, self._dir)):
					relative_path = os.path.join(self._dir, file)
					full_path = os.path.join(self._strip_path, relative_path)
					if os.path.isdir(full_path): self._stack.append(self._stack_element(relative_path, stack_element._include_patterns))
					else:
						match = False
						for include_pattern in stack_element._include_patterns:
							if fnmatch.fnmatchcase(relative_path, include_pattern):
								match = True
								break
						if match:
								for exclude_pattern in self._exclude_patterns:
									if fnmatch.fnmatchcase(relative_path, exclude_pattern):
										match = False
										break
						if match: self._files.append(file)
				self._index = 0
			else:
				# got a filename
				return self.file(self._strip_path, os.path.join(self._dir, file))

	class _stack_element:
		def __init__(self, dir, include_patterns):
			self._dir = dir
			self._include_patterns = include_patterns

	def _split_wilcards(self, path):
		components = []
		head = path
		while True:
			head, tail = os.path.split(head)
			components.append(tail)
			if not len(head): break
		components.reverse()
		result = []
		for component in components:
			if '*' in component: break
			result.append(component)
		return os.path.sep.join(result)
	
	class file:
		def __init__(self, strip, relative):
			self._strip = strip
			self._relative = relative
		def full(self): return os.path.join(self._strip, self._relative)
		def strip(self): return self._strip
		def relative(self): return self._relative

def print_all_nodes(dirnode):
	'prints all the scons nodes that are children of this node, recursively.'
	import SCons.Node.FS
	if type(dirnode) == type(''): dirnode = SCons.Node.FS.default_fs.Dir(dirnode)
	dt = type(SCons.Node.FS.default_fs.Dir('.'))
	for f in dirnode.all_children():
		if type(f) == dt:
			#print '%s/' % str(f)
			print_all_nodes(f)
		else: print '%s' % (str(f))

def glob(includes = ['*'], excludes = None, dir = '.'):
	"""
	similar to glob.glob, except globs SCons nodes, and thus sees generated files and files from build directories.
	Basically, it sees anything SCons knows about.
	A key subtlety is that since this function operates on generated nodes as well as source nodes on the filesystem,
	it needs to be called after builders that generate files you want to include.
	
	It will return both Dir entries and File entries
	"""
	
	def fn_filter(node):
		fn = os.path.basename(str(node))
		match = False
		for include in includes:
			if fnmatch.fnmatchcase(fn, include):
				match = True
				break
		if match and excludes is not None:
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
		"""
		Checks first to see if the node is a file or a dir, then creates the appropriate node.
		(code seems redundant, if the node is a node, then shouldn't it just be left as is?)
		"""
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
