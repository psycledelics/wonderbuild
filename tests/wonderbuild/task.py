#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from signature import Sig
from cmd import exec_subprocess

class Signed(object):
	def __init__(self):
		self.sig = None

	def get_sig(self): return Sig()
	sig = property(get_sig)

class Task(Signed):
	def __init__(self, in_nodes, out_nodes):
		self.in_nodes = in_nodes
		self.out_nodes = out_nodes
		self.processed = False

	def dyn_deps(self): pass
			
	def process(self): pass

	def get_sig(self):
		sig = Signed.Sig(self)
		for n in self.in_nodes: sig.update(n.sig)
		return sig
		
class FuncTask(Task):
	def __init__(self, in_nodes, func, out_nodes):
		Task.__init__(self, in_nodes, out_nodes)
		self.func = func
		
	def process(self): self.func()

	def get_sig(self):
		sig = Task.get_sig(self)
		sig.update(self.func.code)
		return sig
		
class CmdTask(Task):
	def __init__(self, in_nodes, env, cmd_args, out_nodes):
		Task.__init__(self, in_nodes, out_nodes)
		self.env = env
		self.cmd_args = cmd_args
		
	def process(self):
		r = exec_subprocess(self.env, self.cmd_args)
		if r != 0: raise r

	def get_sig(self):
		sig = Task.get_sig(self)
		for k, v in self.env:
			sig.update(k)
			sig.update(v)
		sig.update(self.cmd_args)
		return sig
