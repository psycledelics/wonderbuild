#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

try:
	from hashlib import md5
except ImportError:
	from md5 import md5

class Sig:
	def __init__(self):
		self._impl = md5()
	def update(self, s): self._impl.update(s)
	def digest(self): return self._impl.digest()

class Node:
	def __init__(self, name):
		self._name = name
		self._dep_nodes = []

	def compute_sig(self):
		s = Sig()
		s.update(self._cmd_args)
		for n in self._in_nodes: s.update(n.sig())
		return s.digest()
		
	def sig(self):
		try: return self._sig
		except AttributeError:
			self._sig = self.compute_sig()
			return self._sig

	def compute_sig(self):
		s = Sig()
		s.update(hash_file(self.abspath()))
		for n in self._dep_nodes: s.update(n.sig())
		return s.digest()
	
class AliasNode(Node):
	def __init__(self, name, nodes):
		Node.__init__(self, name)
		self._dep_nodes = nodes

class ValueNode(Node):
	def __init__(self, parent_node, value):
		Node.__init__(self, parent_node, name = None)
		self._value = value

	def compute_sig(self):
		self._sig = Sig(self._value)

class FSNode(Node):
	def __init__(self, parent_node, name):
		Node.__init__(self, name)
		self._parent = parent_node
	
class DirFSNode(FSNode):
	"""A dir is up-to-date if all of its children nodes are up-to-date"""
	def __init__(self, parent_node, name):
		FSNode.__init__(self, parent_node, name)
		self._children = []

class FileFSNode(FSNode):
	def __init__(self, parent_node, name):
		FSNode.__init__(self, parent_node, name)

class FSTree:
	def __init__(self):
		self._nodes = []

