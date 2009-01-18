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

class ClientCfg(object):
	def __init__(self, project):
		self.project = project
		self.defines = {}
		self.include_paths = []
		self.cxx_flags = []
		self.lib_paths = []
		self.libs = []
		self.static_libs = []
		self.shared_libs = []
		self.ld_flags = []
		self.pkgs = []
		
	def apply(self, other):
		self.defines.update(other.defines)
		for i in other.include_paths: self.include_paths.append(i)
		for f in other.cxx_flags: self.cxx_flags.append(f)
		for i in other.lib_paths: self.lib_paths.append(i)
		for l in other.libs: self.libs.append(l)
		for l in other.static_libs: self.static_libs.append(l)
		for l in other.shared_libs: self.shared_libs.append(l)
		for f in other.ld_flags: self.ld_flags.append(f)
		for p in other.pkgs: self.pkgs.append(p)

	def clone(self):
		c = self.__class__(self.project)
		c.apply(self)
		return c
		
class BuildCfg(ClientCfg):
	def __init__(self, project):
		ClientCfg.__init__(self, project)
		self.cxx_prog = None
		self.pic = None
		self.includes = []
		self.ld_prog = None
		self.ar_prog = None
		self.ranlib_prog = None
		self.shared = None
		self.impl = None
		self.kind = self.version = None
		self.debug = False
		self.optim = None
		self.check_missing = False
	
	def apply(self, other):
		ClientCfg.apply(self, other)
		self.cxx_prog = other.cxx_prog
		self.pic = other.pic
		for i in other.includes: self.includes.append(i)
		self.ld_prog = other.ld_prog
		self.ar_prog = other.ar_prog
		self.ranlib_prog = other.ranlib_prog
		self.shared = other.shared
		self.impl = other.impl
		self.kind = other.kind
		self.version = other.version

	@property
	def _common_sig(self):
		try: return self.__common_sig
		except AttributeError:
			sig = Sig(self.impl.common_env_sig)
			for name in ('PATH',):
				e = os.environ.get(name, None)
				if e is not None: sig.update(e)
			sig.update(self.kind)
			sig.update(self.version)
			sig.update(str(self.debug))
			sig.update(str(self.optim))
			for p in self.pkgs: sig.update(p.sig)
			sig = self.__common_sig = sig.digest()
			return sig
		
	@property
	def cxx_sig(self):
		try: return self._cxx_sig
		except AttributeError:
			sig = Sig(self._common_sig)
			sig.update(self.cxx_prog)
			sig.update(str(self.pic))
			for k, v in self.defines.iteritems():
				sig.update(k)
				if v is not None: sig.update(v)
			for i in self.include_paths: sig.update(i.abs_path)
			for i in self.includes: sig.update(i.abs_path)
			for f in self.cxx_flags: sig.update(f)
			sig.update(self.impl.cxx_env_sig)
			sig = self._cxx_sig = sig.digest()
			return sig

	@property
	def _common_mod_sig(self):
		try: return self.__common_mod_sig
		except AttributeError:
			sig = Sig(self._common_sig)
			sig.update(str(self.shared))
			for p in self.lib_paths: sig.update(p.path)
			for l in self.libs: sig.update(l)
			for l in self.static_libs: sig.update(l)
			for l in self.shared_libs: sig.update(l)
			sig.update(self.impl.common_mod_env_sig)
			sig = self.__common_mod_sig = sig.digest()
			return sig

	@property
	def ar_ranlib_sig(self):
		try: return self._ar_ranlib_sig
		except AttributeError:
			sig = Sig(self._common_mod_sig)
			sig.update(self.ar_prog)
			sig.update(self.ranlib_prog)
			sig.update(self.impl.ar_ranlib_env_sig)
			sig = self._ar_ranlib_sig = sig.digest()
			return sig

	@property
	def ld_sig(self):
		try: return self._ld_sig
		except AttributeError:
			sig = Sig(self._common_mod_sig)
			sig.update(self.ld_prog)
			for f in self.ld_flags: sig.update(f)
			sig.update(self.impl.ld_env_sig)
			sig = self._ld_sig = sig.digest()
			return sig

	@property
	def cxx_args(self):
		try: return self._cxx_args
		except AttributeError:
			args = self._cxx_args = self.impl.cfg_cxx_args(self)
			if __debug__ and is_debug: debug('cfg: cxx: build: cxx: ' + str(args))
			return args

	@property
	def ld_args(self):
		try: return self._ld_args
		except AttributeError:
			args = self._ld_args = self.impl.cfg_ld_args(self)
			if __debug__ and is_debug: debug('cfg: cxx: build: ld: ' + str(args))
			return args

	@property
	def ar_ranlib_args(self):
		try: return self._ar_ranlib_args
		except AttributeError:
			args = self._ar_ranlib_args = self.impl.cfg_ar_ranlib_args(self)
			if __debug__ and is_debug: debug('cfg: cxx: build: ar ranlib: ' + str(args))
			return args

class UserCfg(Cfg, BuildCfg):
	_cxx_options = set([
		'--cxx=',
		'--cxx-flags=',
		'--cxx-debug=',
		'--cxx-optim=',
		'--cxx-pic='
	])

	_mod_options = set([
		'--cxx-mod-shared=',
		'--cxx-mod-ld=',
		'--cxx-mod-ld-flags=',
		'--cxx-mod-ar=',
		'--cxx-mod-ranlib='
	])
	
	_options = _cxx_options | _mod_options | set([
		'--cxx-check-missing='
	])
	
	def help(self):
		help['--cxx=']                  = ('--cxx=<prog>', 'use <prog> as c++ compiler')
		help['--cxx-flags=']            = ('--cxx-flags=[flags]', 'use specific c++ compiler flags')
		help['--cxx-debug=']            = ('--cxx-debug=<yes|no>', 'make the c++ compiler produce debugging information or not', 'no')
		help['--cxx-optim=']            = ('--cxx-optim=<level>', 'use c++ compiler optimisation <level>')
		help['--cxx-pic=']              = ('--cxx-pic=<yes|no>', 'make the c++ compiler emit pic code rather than non-pic code for static libs and programs (always pic for shared libs)', 'no (for static libs and programs)')
		help['--cxx-mod-shared=']       = ('--cxx-mod-shared=<yes|no>', 'build and link shared libs (rather than static libs)', 'yes unless pic is set explicitly to no')
		help['--cxx-mod-ld=']           = ('--cxx-mod-ld=<prog>', 'use <prog> as shared lib and program linker')
		help['--cxx-mod-ld-flags=']     = ('--cxx-mod-ld-flags=[flags]', 'use specific linker flags')
		help['--cxx-mod-ar=']           = ('--cxx-mod-ar=<prog>', 'use <prog> as static lib archiver', 'ar')
		help['--cxx-mod-ranlib=']       = ('--cxx-mod-ranlib=<prog>', 'use <prog> as static lib archive indexer', 'ranlib (or via ar s flag for gnu ar)')
		help['--cxx-check-missing=']    = ('--cxx-check-missing=<yes|no>', 'check for missing built files (rebuilds files you manually deleted in the build dir)', 'no')

	def __init__(self, project):
		Cfg.__init__(self, project)
		BuildCfg.__init__(self, project)

		try:
			old_sig, self.check_missing, \
			self.kind, self.version, \
			self.cxx_prog, self.cxx_flags, self.pic, self.optim, self.debug, \
			self.shared, self.ld_prog, self.ld_flags, \
			self.ar_prog, self.ranlib_prog = \
				self.project.state_and_cache[self.__class__.__name__ + '2'] # XXX remove '2' (below too)
		except KeyError: parse = True
		else: parse = old_sig != self.options_sig

		if parse:
			if __debug__ and is_debug: debug('cfg: cxx: user: parsing options')
			self.shared = self.pic = self.optim = None
			self.debug = self.check_missing = False
			cxx_prog = cxx_flags = ld_prog = ld_flags = ar_prog = ranlib_prog = False
			for o in options:
				if o.startswith('--cxx='): self.cxx_prog = o[len('--cxx='):]; cxx_prog = True
				elif o.startswith('--cxx-flags='): self.cxx_flags = o[len('--cxx-flags='):].split(); cxx_flags = True
				elif o.startswith('--cxx-pic='): self.pic = o[len('--cxx-pic='):] != 'no'
				elif o.startswith('--cxx-optim='): self.optim = o[len('--cxx-optim='):]
				elif o.startswith('--cxx-debug='): self.debug = o[len('--cxx-debug='):] == 'yes'
				elif o.startswith('--cxx-mod-shared'): self.shared = o[len('--cxx-mod-shared='):] != 'no'
				elif o.startswith('--cxx-mod-ld='): self.ld_prog = o[len('--cxx-mod-ld='):]; ld = True
				elif o.startswith('--cxx-mod-ld-flags='): self.ld_flags = o[len('--cxx-mod-ld-flags='):].split(); ld_flags = True
				elif o.startswith('--cxx-mod-ar='): self.ar_prog = o[len('--cxx-mod-ar='):]; ar_prog = True
				elif o.startswith('--cxx-mod-ranlib='): self.ranlib_prog = o[len('--cxx-mod-ranlib='):]; ranlib_prog = True
				elif o.startswith('--cxx-check-missing='): self.check_missing = o[len('--cxx-check-missing='):]  == 'yes'
			if self.pic is None:
				if self.shared is None: self.shared = True
				self.pic = False
			elif self.shared is None: self.shared = self.pic

			if not cxx_prog: self.cxx_prog = 'c++'

			self.print_desc('checking for c++ compiler')
			r, out, err = exec_subprocess_pipe([self.cxx_prog, '-dumpversion'], silent = True)
			if r != 0:
				if not silent: self.print_result_desc('not gcc\n', '31')
				self.kind = None
				self.version = None
			else:
				self.kind = 'gcc'
				self.version = out.rstrip('\n')
				self.ld_prog = self.cxx_prog
				ld_prog = True
				import gcc2
				self.impl = gcc2.Impl()
			self.print_result_desc(str(self.kind) + ' version ' + str(self.version) + '\n', '32')

			if not cxx_flags:
				flags = os.environ.get('CXXFLAGS', None)
				if flags is not None: self.cxx_flags = flags.split()
				else: self.cxx_flags = []

			if not ld_prog: self.ld_prog = self.impl.ld_prog
			if not ld_flags:
				flags = os.environ.get('LDFLAGS', None)
				if flags is not None: self.ld_flags = flags.split()
				else: self.ld_flags = []

			if not ar_prog: self.ar_prog = self.impl.ar_prog
			if not ranlib_prog: self.ranlib_prog = self.impl.ranlib_prog
			
			# XXX remove '2' (above too)
			self.project.state_and_cache[self.__class__.__name__ + '2'] = \
				self.options_sig, self.check_missing, \
				self.kind, self.version, \
				self.cxx_prog, self.cxx_flags, self.pic, self.optim, self.debug, \
				self.shared, self.ld_prog, self.ld_flags, \
				self.ar_prog, self.ranlib_prog

		elif self.kind == 'gcc':
			import gcc2
			self.impl = gcc2.Impl()

		if self.impl is None: raise Exception, 'unsupported c++ compiler'

	def clone(self):
		c = BuildCfg(self.project)
		c.apply(self)
		return c

class BuildCheck(object):
	def __init__(self, name, base_cfg):
		self.name = name
		self._base_cfg

	def apply_to(self, cfg): pass

	@property
	def source(self): pass

	@property
	def cfg(self):
		try: return self._cfg
		except AttributeError:
			self._cfg = self._base_cfg.clone()
			self.apply_to(self._cfg)
			return self._cfg
		
	@property
	def project(self): return self._base_cfg.project
	
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
				self._result = self.cfg.impl.process_cxx() == 0
				return self._result
				
class CxxTask(Task):
	def __init__(self, mod_task):
		Task.__init__(self, mod_task.project)
		self.mod_task = mod_task
		self.sources = []

	@property
	def cfg(self): return self.mod_task.cfg

	def __str__(self): return ' '.join([str(s) for s in self.sources])

	@property
	def uid(self): return self.mod_task.uid

	@property
	def target_dir(self): return self.mod_task.target_dir

	def need_process(self): return True

	def process(self):
		lock = self.target_dir.lock
		lock.acquire()
		try: self.target_dir.make_dir()
		finally: lock.release()
		if not silent:
			if self.cfg.pic: pic = 'pic'; color = '7;1;34'
			else: pic = 'non-pic'; color = '7;34'
			self.print_desc('batch-compiling ' + pic + ' objects from c++ ' + str(self), color)
		self._actual_sources = []
		self.target_dir.actual_children # not needed, just an optimisation
		for s in self.sources:
			node = self.target_dir.node_path(self.mod_task._unique_base_name(s))
			if not node.exists:
				f = open(node.path, 'wb')
				try: f.write('#include "%s"\n' % s.rel_path(self.target_dir))
				finally: f.close()
			self._actual_sources.append(node)
		self.cfg.impl.process_cxx_task(self)
		Task.process(self)

class ModTask(Task):
	class Kinds(object):
		PROG = 0
		LIB = 1
		LOADABLE = 2

	def __init__(self, name, kind, base_cfg, aliases = None):
		Task.__init__(self, base_cfg.project, aliases)
		self.name = name
		self.sources = []
		self.kind = kind
		self.cfg = base_cfg.clone()
		if self.kind == ModTask.Kinds.PROG:
			self.cfg.shared = False
			self.ld = True
		else:
			self.ld = self.cfg.shared
			if self.cfg.shared and not self.cfg.pic:
				debug('cfg: cxx: mod: shared lib => overriding cfg to pic')
				self.cfg.pic = True

	def __str__(self): return str(self.target)

	@property
	def uid(self): return self.name

	@property
	def target(self):
		try: return self._target
		except AttributeError:
			self._target = self.project.bld_node.\
				node_path('modules').\
				node_path(self.name).\
				node_path(self.cfg.impl.mod_task_target_name(self))
			return self._target

	@property
	def target_dir(self): return self.target.parent

	def dyn_in_tasks(self, sched_context):
		changed_sources = []
		try: state = self.project.task_states[self.uid]
		except KeyError:
			if __debug__ and is_debug: debug('task: no state: ' + str(self))
			self.project.task_states[self.uid] = None, None, {}
			changed_sources = self.sources
		else:
			if state[1] != self.cfg.cxx_sig:
				if __debug__ and is_debug: debug('task: cxx sig changed: ' + str(self))
				changed_sources = self.sources
			else:
				implicit_deps = state[2]
				for s in self.sources:
					try: old_sig, deps = implicit_deps[s]
					except KeyError:
						# This is a new source.
						changed_sources.append(s)
						continue
					try: sigs = [dep.sig for dep in deps]
					except OSError:
						# A cached implicit dep does not exist anymore.
						if __debug__ and is_debug: debug('cpp: deps not found: ' + str(s))
						changed_sources.append(s)
						continue
					sigs.sort()
					sig = Sig(''.join(sigs)).digest()
					if old_sig != sig:
						# The cached implicit deps changed.
						if __debug__ and is_debug: debug('cpp: deps changed: ' + str(s))
						changed_sources.append(s)
						continue
					if self.cfg.check_missing:
						try: self.target_dir.actual_children # not needed, just an optimisation
						except OSError: pass
						o = self.target_dir.node_path(self._obj_name(s))
						if not o.exists:
							if __debug__ and is_debug: debug('task: target removed: ' + str(o))
							changed_sources.append(s)
							continue
					if __debug__ and is_debug: debug('task: skip: no change: ' + str(s))
				if not self.cfg.check_missing: self.target_dir.forget()
		if len(changed_sources) != 0:
			batches = []
			for i in xrange(sched_context.thread_count): batches.append([])
			i = 0
			for s in changed_sources:
				batches[i].append(s)
				i = (i + 1) % sched_context.thread_count
			for b in batches:
				if len(b) == 0: break
				t = CxxTask(self)
				t.sources = b
				self.add_in_task(t)
		self._changed_sources = changed_sources
		return self.in_tasks

	def need_process(self):
		if self.cfg.check_missing and not self.target.exists:
			if __debug__ and is_debug: debug('task: target removed: ' + str(self))
			self._changed_sources = self.sources
			return True
		if len(self._changed_sources) != 0: return True
		state = self.project.task_states[self.uid]
		if state[0] != self._mod_sig:
			if __debug__ and is_debug: debug('task: mod sig changed: ' + str(self))
			self._changed_sources = self.sources
			return True
		for t in self.in_tasks:
			if t.processed:
				try: ld = t.ld
				except AttributeError: continue # not a lib task
				if True:#if not ld: when a dependant lib changes its kind from static to shared, we actually need to relink.
					# TODO To be able to detect when a dependant lib changes its kind,
					# we'd need to store these kinds in the task state.
					# For now, we always relink, even when the dependent lib was already a shared lib before.
					if __debug__ and is_debug: debug('task: in task changed: ' + str(self) + ' ' + str(t))
					return True
		if __debug__ and is_debug: debug('task: skip: no change: ' + str(self))
		return False

	def process(self):
		if not silent:
			if not self.ld: desc = 'archiving and indexing static lib'; color = '7;36'
			elif self.kind == ModTask.Kinds.PROG:
				if not self.cfg.pic: desc = 'linking non-pic program'; color = '7;32'
				else: desc = 'linking pic program'; color = '7;1;32'
			elif self.kind == ModTask.Kinds.LOADABLE: desc = 'linking loadable module'; color = '7;1;34'
			else: desc = 'linking shared lib'; color = '7;1;33'
			self.print_desc(desc + ' ' + str(self), color)
		if self.ld: sources = self.sources
		else: sources = self._changed_sources
		self.cfg.impl.process_mod_task(self, [self._obj_name(s) for s in sources])
		implicit_deps = self.project.task_states[self.uid][2]
		if len(implicit_deps) > len(self.sources):
			# remove old sources from implicit deps dictionary
			sources_states = {}
			for s in self.sources: sources_states[s] = implicit_deps[s]
		else: sources_states = implicit_deps
		self.project.task_states[self.uid] = self._mod_sig, self.cfg.cxx_sig, sources_states #XXX move cxx_sig into obj sig
		Task.process(self)

	def _unique_base_name(self, source):
		return source.rel_path(self.project.src_node).replace(os.pardir, '_').replace(os.sep, ',')

	def _obj_name(self, source):
		name = self._unique_base_name(source)
		return name[:name.rfind('.')] + self.cfg.impl.cxx_task_target_ext

	@property
	def _mod_sig(self):
		if self.ld: return self.cfg.ld_sig
		else: return self.cfg.ar_ranlib_sig

class CxxPreCompileTask(Task):
	def __init__(self, header, cfg):
		Task.__init__(self, cfg.project)
		self.cfg = cfg

	@property
	def header(self): pass

	def apply_to_(self, cfg): cfg.includes.append(self.header)

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
				else:
					dep_sigs.sort()
					dep_sig = Sig(''.join(dep_sigs)).digest()
					if old_dep_sig != sig:
						# The cached implicit deps changed.
						if __debug__ and is_debug: debug('cpp: deps changed: ' + str(self.header))
						changed = True
		if __debug__ and is_debug and not changed: debug('task: skip: no change: ' + str(self.header))
		return changed
