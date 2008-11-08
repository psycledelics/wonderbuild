#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from import signature import Signed, file_sig

class Node(Signed):
	def __init__(self, name):
		self._name = name
		self._dep_nodes = []

	def update_sig(self, sig):
		'implements Signed.update_sig'
		for n in self._dep_nodes: n.update_sign(sig)
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
		
	def abspath(self): pass

	def update_sig(self, sig):
		Node.update_sig(self, sig)
		file_sig(sig, self.abspath())
	
class DirFSNode(FSNode):
	'A dir is up-to-date if all of its children nodes are up-to-date'
	def __init__(self, parent_node, name):
		FSNode.__init__(self, parent_node, name)
		self._children = []

	def update_sig(self, sig):
		FSNode.update_sig(self, sig)
		for n in self._children: n.update_sig(sig)

class FileFSNode(FSNode):
	def __init__(self, parent_node, name):
		FSNode.__init__(self, parent_node, name)

class FSTree:
	def __init__(self):
		self._nodes = []

