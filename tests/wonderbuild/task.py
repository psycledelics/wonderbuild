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
	def __init__(self):
		self.in_tasks = []
		self.in_nodes = []
		self.out_nodes = []
		self.processed = False

	def process(self): pass

	def get_sig(self):
		sig = Signed.Sig(self)
		for n in self.in_nodes: sig.update(n.sig)
		return sig
		
class CmdTask(Task):
	def __init__(self):
		Task.__init__(self)
		self.env = None
		self.cmd_args = None
		
	def process(self):
		r = exec_subprocess(self.env, self.cmd_args)
		if r != 0: raise r

	def get_sig(self):
		sig = Task.get_sig(self)
		for k, v in self.env:
			sig.update(k)
			sig.update('\0')
			sig.update(v)
			sig.update('\0')
		sig.update(self.cmd_args)
		return sig

class ObjTask(Cmd):
	def __init__(self):
		Cmd.__init__(self, cxx)
		self.in_nodes = [cxx]
		self.out_nodes = [cxx.change_ext('cpp', 'o')]
		self.cmd_args = ['c++', '-o', self.out_nodes[0], '-c', self.in_nodes[0]]
		
class LibTask(Cmd):
	def __init__(self, objs):
		Cmd.__init__(self)
		self.in_nodes = objs

	def dyn_deps(self):
		for o in self.in_nodes:
			self.
	
	def process(self):
		self.cmd_args = ['c++', '-o', self.out_nodes[0], '-c', self.in_nodes[0]]
		self.in_nodes.append(n)
			t = ObjTask()
			t.in_nodes = [n]
			t.out_nodes = [
