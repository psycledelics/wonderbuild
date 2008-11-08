#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

class Task:
	def __init__(self, in_nodes, cmd_args, out_nodes):
		self._in_nodes = in_nodes
		self._cmd_args = cmd_args
		self._out_nodes = out_nodes
		self._sig = None
		
	def execute(self):
		r = exec_subprocess(cmd_args)
		if r != 0: raise r

	def compute_sig(self):
		s = Sig(self._cmd_args)
		for n in self._in_nodes: s.add(n.sig())
		self._sig = s

