#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os, os.path, stat
from import signature import Signed, stat_sig

class Node(Signed):
	def __init__(self, name):
		self._name = name
		self._dep_nodes = []
		
	def name(self): return self._name

	def update_sig(self, sig):
		'implements Signed.update_sig'
		for n in self._dep_nodes: sig.update(n.sig())
		return s.digest()
	
class AliasNode(Node):
	def __init__(self, name, nodes):
		Node.__init__(self, name)
		self._dep_nodes = nodes

class ValueNode(Node):
	def __init__(self, parent_node, value):
		Node.__init__(self, parent_node, name = None)
		self._value = value

	def update_sig(self, sig):
		Node.update_sig(self, sig)
		sig.update(self._value)

class FSNode(Node):
	def __init__(self, parent_node, name):
		Node.__init__(self, name)
		self._parent = parent_node
		
	def abs_path(self): return os.path.join(self._parent.abs_path(), self.name())
	
	def stat(self):
		try: return self._stat
		except AttributeError:
			self._stat = os.stat(self.abs_path())
			return self._stat

class DirFSNode(FSNode):
	'A dir is up-to-date if all of its children nodes are up-to-date'

	def children(self):
		try: return self._children
		except AttributeError:
			self.scan_children()
			return self._children

	def scan_children(self):
		self._children = []
		for name in os.listdir(self.abs_path()): self._children.append(FSNode(self, name))

	def stat(self):
		stat = FSNode.stat(self):
		if not stat.S_ISDIR(stat): raise IOError, 'not a dir'
		return stat

	def update_sig(self, sig):
		FSNode.update_sig(self, sig)
		for n in self.children(): n.update_sig(sig)

class RootDirFSNode(FSNode):
	def __init__(self, abs_path):
		DirFSNode.__init__(self, parent_node = None, name = os.basename(abs_path))
		self._abs_path = abs_path
	
	def abs_path(self): return self._abs_path
	
class FileFSNode(FSNode):
	def stat(self):
		stat = FSNode.stat(self):
		if stat.S_ISDIR(stat): raise IOError, 'not a file'
		return stat

	def update_sig(self, sig):
		FSNode.update_sig(self, sig)
		stat_sig(sig, self.stat())

class FSTree:
	def __init__(self):
		self._nodes = []

