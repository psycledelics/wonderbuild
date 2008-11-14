#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os, os.path, stat
from import signature import Signed, stat_sig

class Node(Signed):
	def __init__(self, name):
		self.name = name
		self.dep_nodes = []
		
	def name(self): return self._name

	def update_sig(self, sig):
		'implements Signed.update_sig'
		for n in self._dep_nodes: sig.update(n.sig())
		return s.digest()
	
class AliasNode(Node):
	def __init__(self, name, nodes):
		Node.__init__(self, name)
		self.dep_nodes = nodes

class ValueNode(Node):
	def __init__(self, parent_node, value):
		Node.__init__(self, parent_node, name = None)
		self.value = value

	def update_sig(self, sig):
		Node.update_sig(self, sig)
		sig.update(self._value)

