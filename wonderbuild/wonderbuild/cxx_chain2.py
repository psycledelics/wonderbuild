#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2007-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os, threading
#python 2.5.0a1 from __future__ import with_statement

from options import options, known_options, help
from logger import out, is_debug, debug, colored, silent
from signature import Sig
from cfg import Cfg
from task import Task, exec_subprocess_pipe

class ClientCxxCfg(object):
	def __init__(self, project):
		self.project = project
		self.include_paths = []
		self.defines = {}
		self.flags = []
		self.pkgs = []
		
	def apply(self, other):
		for i in other.include_paths: self.include_paths.append(i)
		self.defines.update(other.defines)
		for f in other.flags: self.flags.append(f)
		for p in other.pkgs: self.pkgs.append(p)
		
	def clone(self):
		c = self.__class__(self.project)
		c.apply(self)
		return c
		
class BuildCxxCfg(ClientCxxCfg):
	def __init__(self, project)
		ClientCxxCfg.__init__(self, project)
		self.cxx_prog = 'g++'
		self.pic = True
		self.includes = []
		self.impl = None
	
	def apply(self, other):
		ClientCxxCfg.apply(self, other)
		self.cxx_prog = other.cxx_prog
		self.pic = other.pic
		for i in other.includes: self.includes.append(i)
		self.impl = other.impl

	def apply_client(self, other): ClientCxxCfg.apply(self, other)

class ClientLinkCfg(object)
	def __init__(self, project)
		self.project = project
		self.lib_paths = []
		self.libs = []
		self.flags = []
		self.pkgs = []

class BuildLinkCfg(ClientLinkCfg)
	def __init__(self, project):
		ClientLinkCfg.__init__(self, project)
		self.ld_prog = 'g++'
		self.shared = True

class BuildCheck(object):
	def __init__(self, name, base_build_cfg)
		self.name = name
		self.base_build_cfg

	@property
	def source(self): pass

	@property
	def build_cfg(self): pass
	
	def apply_to(self, build_cfg): pass

	@property
	def project(self): return self.base_build_cfg.project
	
	@property
	def uid(self): return self.name
	
	@property
	def result(self):
		try: return self._result
		except AttributeError:
			n = self.project.bld_node.node_path('checks').node_path(self.name)
			changed = False
			if not n.exists: changed = True
			try: old_sig = self.project.state_and_cache[self.uid]
			except KeyError: changed = True
			else:
				sig = Sig(self.source)
				sig.update(self.build.sig)
				sig = sig.digest()
				if old_sig != sig: changed = True
			if changed:
				n.make_dir()
				n = n.node_path('source.cpp')
				f = open(n.path, 'w')
				try: f.write(self.source)
				finally: f.close()
				self._result = self.build_cfg.cxx.impl.process_cxx() == 0
				return self._result
				
class CxxPreCompileTask(Task):
	def __init__(self, build_cxx_cfg, header):
		Task.__init__(self, build_cxx_cfg.project)
		self.cfg = build_cxx_cfg
		self.header = header

	@property
	def impl(self): return self.cfg.impl

	def __str__(self): return str(header)

	@property
	def uid(self): return self.header #XXX

	@property
	def target_dir(self):
		try: return self._target_dir
		except AttributeError:
			self._target_dir = self.project.bld_node.\
				node_path('precompiled-headers').\
				node_path(self.header.rel_path(self.project.src_node)) #XXX
			return self._target_dir

	def need_process(self):
		changed = False
		try: old_cfg_sig, deps, old_dep_sig = self.project.task_states[self.uid]
		except KeyError:
			if __debug__ and is_debug: debug('task: no state: ' + str(self))
			self.project.task_states[self.uid] = None, None, None
			changed = True
		else:
			if old_cfg_sig != self.cfg.sig:
				if __debug__ and is_debug: debug('task: cxx sig changed: ' + str(self))
				changed = True
			else:
				try: dep_sigs = [dep.sig for dep in deps]
				except OSError:
					# A cached implicit dep does not exist anymore.
					if __debug__ and is_debug: debug('cpp: deps not found: ' + str(self.header))
					changed = True
					break
				dep_sigs.sort()
				dep_sig = Sig(''.join(dep_sigs)).digest()
				if old_dep_sig != sig:
					# The cached implicit deps changed.
					if __debug__ and is_debug: debug('cpp: deps changed: ' + str(self.header))
					changed = True
					break
				if __debug__ and is_debug: debug('task: skip: no change: ' + str(self.header))
		return changed
