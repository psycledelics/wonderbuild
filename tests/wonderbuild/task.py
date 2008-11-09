#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from signature import Signed
from cmd import exec_subprocess

class Task(Signed):
	def __init__(self, in_nodes, out_nodes):
		self._in_nodes = in_nodes
		self._out_nodes = out_nodes

	def dyn_deps(self): pass
			
	def process(self): pass

	def update_sig(self, sig):
		'implements Signed.update_sig'
		for n in self._in_nodes: sig.update(n.sig())
		
class FuncTask(Task):
	def __init__(self, in_nodes, func, out_nodes):
		Task.__init__(self, in_nodes, out_nodes)
		self._func = func
		
	def process(self):
		self._func()

	def update_sig(self, sig):
		Task.update_sig(self, sig)
		sig.update(self._func.code)

class CmdTask(Task):
	def __init__(self, in_nodes, env, cmd_args, out_nodes):
		Task.__init__(self, in_nodes, out_nodes)
		self._env = env
		self._cmd_args = cmd_args
		
	def process(self):
		r = exec_subprocess(self._env, self._cmd_args)
		if r != 0: raise r

	def update_sig(self, sig):
		Task.update_sig(self, sig)
		for (k,v) in self._env:
			sig.update(k)
			sig.update(v)
		sig.update(self._cmd_args)

