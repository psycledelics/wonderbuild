#! /usr/bin/env python

class RootProject: pass
class Project : pass

class Contexes:
	def check_and_build(self):
		'when performing build checks, or building the sources'
		pass
		
	def build(self):
		'when building the sources'
		pass
		
	def source(self):
		'when building a tarball of the sources'
		pass
	
	class client:
		'when used as a dependency'
		
		def uninstalled(self):
			'when not yet installed'
			pass
		
		def installed(self):
			'when installed'
			pass
	

class Cmd: pass
	def cmd(self): pass
	def message(self): pass

class Cxx(Cmd): pass
class GnuCxx(Cxx): pass
class MingwGnuCxx(GnuCxx): pass
class MsCxx(Cxx): pass

class Archiver(Cmd): pass
class GnuArchiver(Archiver): pass
class MsArchiver(Archiver): pass

class ArchiveIndexer(Cmd): pass
class GnuArchiveIndexer(ArchiveIndexer): pass
class MsArchiveIndexer(ArchiveIndexer): pass

class Linker(Cmd): pass
class GnuLinker: pass
class MingwGnuLinker(GnuLinker): pass
class MsLinker(Linker): pass

class Chain:
	def __init(self, compilers, archiver, archive_indexer, linker):
		self._compilers = compilers
		self._archiver = archiver
		self._archive_indexer = archive_indexer
		self._linker = linker

class Node:
	def __init__(self, name):
		self._name = name
		self._dep_nodes = []
		self._sig = None

	def compute_sig(self): pass
	
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

class Sig:
	pass

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

class TaskMaster:
	def __init__(self):
		self._tasks = []
		self._leaf_tasks = []
		self._ready_tasks = []
		self._done_tasks = []

import sys, subprocess

def exec_subprocess(args): return exec_subprocess_3(args)

def exec_subprocess_1(args):
	p = subprocess.Popen(
		args = args,
		stdout = subprocess.PIPE,
		stderr = subprocess.PIPE,
		bufsize = 0,
		shell = False,
		env = {}
	)
	out_eof = err_eof = False
	while not(out_eof and err_eof):
		if not out_eof:
			r = p.stdout.read()
			if not r: out_eof = True
			else: sys.stdout.write(r)
		if not err_eof:
			r = p.stderr.read()
			if not r: err_eof = True
			else: sys.stderr.write(r)
	return p.wait()

def exec_subprocess_2(args):
	p = subprocess.Popen(
		args = args,
		stdout = subprocess.PIPE,
		stderr = subprocess.PIPE,
		bufsize = 0,
		shell = False,
		env = {}
	)
	while p.poll() is None:
		r = p.stdout.readline()
		if len(r) != 0: sys.stdout.write(r)
		r = p.stderr.readline()
		if len(r) != 0: sys.stderr.write(r)
	return p.returncode

def exec_subprocess_3(args):
	p = subprocess.Popen(
		args = args,
		stdout = subprocess.PIPE,
		stderr = subprocess.PIPE,
		bufsize = 0,
		shell = False,
		env = {}
	)
	out, err = p.communicate()
	sys.stdout.write(out)
	sys.stderr.write(err)
	return p.returncode

if __name__ == '__main__':
	args = ['find', '.']
	print args, '\n', exec_subprocess(args)
	#args = ['./x']
	#print args, '\n', exec_subprocess(args)

if False:
	have_cxx_compiler = have_prog('c++')
	if not have_cxx_compiler: have_cxx_compiler = have_prog('g++')
	if not have_cxx_compiler: have_cxx_compiler = have_prog('cl')
	cxx = ValueNode(have_cxx_compiler)
	class M(Module):
		def __init__(self, project):
			Module.__init__(self, project)
			
		def dyn_dep(self):
			cxx = self.project().check_tool('cxx')
			if not cxx: return False
			if not cxx.build_check(
				defines = [],
				includes = [],
				libpath = [],
				libs = ['m'],
				src = '''
					#include <cmath>
					float f() { return std::sin(0); }
				'''
			): return False
			return True
		
	s = Node('src/foo.hpp.in')
	o = Node('++build/src/foo.hpp')
	d = Dependency(o, Dependency.CONTENT, s)
	t = Task([s], ['cp', s.name(), o.name()], [o])
	tm = TaskMaster()
	tm.add_task(t)
	tm.run()
