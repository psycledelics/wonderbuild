#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2007-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os, threading
from collections import deque

from options import options, known_options, help
from logger import out, is_debug, debug, colored, silent
from signature import Sig
from cfg import Cfg
from task import Task
from subprocess_wrapper import exec_subprocess, exec_subprocess_pipe

class ClientCfg(object):
	def __init__(self, project):
		self.project = project
		self.defines = {}
		self.include_paths = deque()
		self.cxx_flags = []
		self.lib_paths = deque()
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
		self.debug = other.debug
		self.optim = other.optim

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

	def print_check(self, desc):
		out.write(colored('34', 'wonderbuild: cfg: ' + desc + ' ...') + '\n')
		out.flush()
		
	def print_check_result(self, desc, result, color):
		out.write(colored('34', 'wonderbuild: cfg: ' + desc + ': ') + colored(color, result) + '\n')
		out.flush()

class UserCfg(Cfg, BuildCfg):
	_options = set([
		'--cxx=',
		'--cxx-flags=',
		'--cxx-debug=',
		'--cxx-optim=',
		'--cxx-pic=',
		'--cxx-mod-shared=',
		'--cxx-mod-ld=',
		'--cxx-mod-ld-flags=',
		'--cxx-mod-ar=',
		'--cxx-mod-ranlib=',
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
				self.project.state_and_cache[self.__class__.__name__]
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

			self._check_compiler(cxx_prog, ld_prog)

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
			
			self.project.state_and_cache[self.__class__.__name__] = \
				self.options_sig, self.check_missing, \
				self.kind, self.version, \
				self.cxx_prog, self.cxx_flags, self.pic, self.optim, self.debug, \
				self.shared, self.ld_prog, self.ld_flags, \
				self.ar_prog, self.ranlib_prog

		elif self.kind == 'gcc':
			import gcc
			self.impl = gcc.Impl()

		if self.impl is None: raise Exception, 'unsupported c++ compiler'

	def _check_compiler(self, cxx_prog, ld_prog):
		if not cxx_prog: self.cxx_prog = 'c++'
		if not silent:
			desc = 'checking for c++ compiler'
			self.print_check(desc)
		r, out, err = exec_subprocess_pipe([self.cxx_prog, '-dumpversion'], silent = True)
		if r != 0:
			if not silent: self.print_check_result(desc, 'not gcc', '31')
			self.kind = None
			self.version = None
		else:
			self.kind = 'gcc'
			self.version = out.rstrip('\n')
			if not ld_prog:
				self.ld_prog = self.cxx_prog
				ld_prog = True
			import gcc
			self.impl = gcc.Impl()
		if not silent: self.print_check_result(desc, str(self.kind) + ' version ' + str(self.version), '32')

	def clone(self):
		c = BuildCfg(self.project)
		c.apply(self)
		return c

class PreCompileTask(Task):
	def __init__(self, name, base_cfg):
		Task.__init__(self, base_cfg.project)
		self.name = name
		self.base_cfg = base_cfg

	@property
	def source_text(self): return '#error ' + str(self.__class__) + ' did not redefine default source text.\n'

	@property
	def cfg(self):
		try: return self._cfg
		except AttributeError:
			self._cfg = self.base_cfg.clone()
			#self._cfg.include_paths.appendleft(self.target_dir)
			return self._cfg

	def apply_to(self, cfg):
		cfg.include_paths.appendleft(self.target_dir)
		cfg.includes.append(self.header)

	def __str__(self): return str(self.header)

	@property
	def uid(self): return self.name

	@property
	def header(self):
		try: return self._header
		except AttributeError:
			self._header = self.project.bld_node.node_path('precompiled').node_path(self.name + '.private.hpp')
			return self._header

	@property
	def target(self):
		try: return self._target
		except AttributeError:
			self._target = self.header.parent.node_path(self.header.name + self.cfg.impl.precompile_task_target_ext)
			return self._target

	@property
	def target_dir(self): return self.target.parent

	def __call__(self, sched_context):
		sched_context.lock.release()
		try:
			changed = False
			try: old_sig, deps, old_dep_sig = self.project.state_and_cache[self.uid]
			except KeyError:
				if __debug__ and is_debug: debug('task: no state: ' + str(self))
				changed = True
			else:
				if old_sig != self.sig:
					if __debug__ and is_debug: debug('task: sig changed: ' + str(self))
					changed = True
				else:
					try: dep_sigs = [dep.sig for dep in deps]
					except OSError:
						# A cached implicit dep does not exist anymore.
						if __debug__ and is_debug: debug('cpp: deps not found: ' + str(self.header))
						changed = True
					else:
						dep_sigs.sort()
						if old_dep_sig != Sig(''.join(dep_sigs)).digest():
							# The cached implicit deps changed.
							if __debug__ and is_debug: debug('cpp: deps changed: ' + str(self.header))
							changed = True
						elif self.cfg.check_missing:
							try: self.target_dir.actual_children # not needed, just an optimisation
							except OSError: pass
							if not self.target.exists:
								if __debug__ and is_debug: debug('task: target removed: ' + str(self.target))
								changed = True
			if not changed:
				if __debug__ and is_debug: debug('task: skip: no change: ' + str(self.header))
			else:
				if not silent: self.print_desc('pre-compiling c++ ' + str(self), color = '7;35')
				dir = self.header.parent
				dir.make_dir(dir.parent)
				f = open(self.header.path, 'w')
				try: f.write(self.source_text); f.write('\n')
				finally: f.close()
				self.cfg.impl.process_precompile_task(self)
				if False:
					# We create a file with a #error to ensure the pch is used.
					f = open(self.header.path, 'w')
					try: f.write('#error pre-compiled header missed\n');
					finally: f.close()
		finally: sched_context.lock.acquire()
		raise StopIteration

	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			sig = Sig(self.source_text)
			sig.update(self.cfg.cxx_sig)
			sig = self._sig = sig.digest()
			return sig

class BatchCompileTask(Task):
	def __init__(self, mod_task, sources):
		Task.__init__(self, mod_task.project)
		self.mod_task = mod_task
		self.sources = sources

	@property
	def cfg(self): return self.mod_task.cfg

	def __str__(self): return ' '.join([str(s) for s in self.sources])

	@property
	def uid(self): return self.mod_task.uid

	@property
	def target_dir(self): return self.mod_task.target_dir

	def __call__(self, sched_context):
		self.target_dir.make_dir()
		sched_context.lock.release()
		try:
			if not silent:
				if self.cfg.pic: pic = 'pic'; color = '7;1;34'
				else: pic = 'non-pic'; color = '7;34'
				self.print_desc('batch-compiling ' + pic + ' objects from c++ ' + str(self), color)
			self._actual_sources = []
			self.target_dir.actual_children # not needed, just an optimisation
			for s in self.sources:
				node = self.target_dir.node_path(self.mod_task._unique_base_name(s))
				if not node.exists:
					f = open(node.path, 'w')
					try: f.write('#include "%s"\n' % s.rel_path(self.target_dir))
					finally: f.close()
				self._actual_sources.append(node)
			self.cfg.impl.process_cxx_task(self)
		finally: sched_context.lock.acquire()
		raise StopIteration

class ModTask(Task):
	class Kinds(object):
		PROG = 0
		LIB = 1
		LOADABLE = 2

	def __init__(self, name, kind, base_cfg, aliases = None):
		Task.__init__(self, base_cfg.project, aliases or (name,))
		self.name = name
		self.kind = kind
		self.cfg = base_cfg.clone()
		if self.kind == ModTask.Kinds.PROG:
			self.cfg.shared = False
			self.ld = True
		else:
			if self.kind == ModTask.Kinds.LOADABLE: self.cfg.shared = True
			self.ld = self.cfg.shared
			if self.cfg.shared and not self.cfg.pic:
				debug('cfg: cxx: mod: shared lib => overriding cfg to pic')
				self.cfg.pic = True
		self.sources = []
		self.dep_lib_tasks = []

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

	def __call__(self, sched_context):
		if len(self.dep_lib_tasks) != 0: yield self.dep_lib_tasks
		changed_sources = []
		try: state = self.project.state_and_cache[self.uid]
		except KeyError:
			if __debug__ and is_debug: debug('task: no state: ' + str(self))
			self.project.state_and_cache[self.uid] = None, None, {}
			changed_sources = self.sources
		else:
			if state[1] != self.cfg.cxx_sig:
				if __debug__ and is_debug: debug('task: cxx sig changed: ' + str(self))
				changed_sources = self.sources
			else:
				implicit_deps = state[2]
				for s in self.sources:
					try: deps, old_dep_sig = implicit_deps[s] # TODO also put self.cfg.cxx_sig
					except KeyError:
						# This is a new source.
						changed_sources.append(s)
						continue
					try: dep_sigs = [dep.sig for dep in deps]
					except OSError:
						# A cached implicit dep does not exist anymore.
						if __debug__ and is_debug: debug('cpp: deps not found: ' + str(s))
						changed_sources.append(s)
						continue
					dep_sigs.sort() # TODO use heapq
					if old_dep_sig != Sig(''.join(dep_sigs)).digest():
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
		need_process = False
		if len(changed_sources) != 0:
			need_process = True
			batches = []
			for i in xrange(sched_context.thread_count): batches.append([])
			i = 0
			for s in changed_sources:
				batches[i].append(s)
				i = (i + 1) % sched_context.thread_count
			tasks = []
			for b in batches:
				if len(b) == 0: break
				tasks.append(BatchCompileTask(self, b))
			yield tasks
		elif self.cfg.check_missing and not self.target.exists:
			if __debug__ and is_debug: debug('task: target removed: ' + str(self))
			changed_sources = sources
			need_process = True
		else:
			state = self.project.state_and_cache[self.uid]
			if state[0] != self._mod_sig:
				if __debug__ and is_debug: debug('task: mod sig changed: ' + str(self))
				changed_sources = self.sources
				need_process = True
			else:
				for t in self.dep_lib_tasks:
					try: processed = t._needed_process
					except AttributeError: continue # not a lib task
					if processed:
							try: ld = t.ld
							except AttributeError: continue # not a lib task
							if True:#if not ld: when a dependant lib changes its kind from static to shared, we actually need to relink.
								# TODO To be able to detect when a dependant lib changes its kind,
								# we'd need to store these kinds in the task state.
								# For now, we always relink, even when the dependent lib was already a shared lib before.
								if __debug__ and is_debug: debug('task: in task changed: ' + str(self) + ' ' + str(t))
								need_process = True
								break
		if not need_process:
			if __debug__ and is_debug: debug('task: skip: no change: ' + str(self))
		else:
			sched_context.lock.release()
			try:
				if not silent:
					if not self.ld: desc = 'archiving and indexing static lib'; color = '7;36'
					elif self.kind == ModTask.Kinds.PROG:
						if not self.cfg.pic: desc = 'linking non-pic program'; color = '7;32'
						else: desc = 'linking pic program'; color = '7;1;32'
					elif self.kind == ModTask.Kinds.LOADABLE: desc = 'linking loadable module'; color = '7;1;34'
					else: desc = 'linking shared lib'; color = '7;1;33'
					self.print_desc(desc + ' ' + str(self), color)
				if self.ld: sources = self.sources
				else: sources = changed_sources
				self.cfg.impl.process_mod_task(self, [self._obj_name(s) for s in sources])
				implicit_deps = self.project.state_and_cache[self.uid][2]
				if len(implicit_deps) > len(self.sources):
					# remove old sources from implicit deps dictionary
					sources_states = {}
					for s in self.sources: sources_states[s] = implicit_deps[s]
				else: sources_states = implicit_deps
				self.project.state_and_cache[self.uid] = self._mod_sig, self.cfg.cxx_sig, sources_states #XXX move cxx_sig into obj sig
			finally: sched_context.lock.acquire()
		if not self.cfg.check_missing: self.target_dir.forget()
		self._needed_process = need_process
		raise StopIteration

	def _unique_base_name(self, source):
		return source.rel_path(self.project.src_node).replace(os.pardir, '_').replace(os.sep, ',')

	def _obj_name(self, source):
		name = self._unique_base_name(source)
		return name[:name.rfind('.')] + self.cfg.impl.cxx_task_target_ext

	@property
	def _mod_sig(self):
		if self.ld: return self.cfg.ld_sig
		else: return self.cfg.ar_ranlib_sig

class PkgConfigCheckTask(Task):
	def __init__(self, name, project):
		Task.__init__(self, project)
		self.name = name

	def apply_to(self, cfg): cfg.pkgs.append(self.name)

	@property
	def uid(self): return self.name

	def __call__(self, sched_context):
		try: self._result
		except AttributeError:
			sched_context.lock.release()
			try: self.result
			finally: sched_context.lock.acquire()
		raise StopIteration

	@property
	def result(self):
		try: return self._result
		except AttributeError:
			changed = False
			try: old_sig, self._result = self.project.state_and_cache[self.uid]
			except KeyError: changed = True
			else:
				if old_sig != self.sig: changed = True
			if not changed:
				if __debug__ and is_debug: debug('task: skip: no change: ' + self.name)
			else:
				desc = 'checking for ' + self.name
				if not silent: self.print_check(desc)
				self._result = 0 == exec_subprocess(args = ['pkg-config', '--exists', self.name])
				self.project.state_and_cache[self.uid] = self.sig, self._result
				if not silent:
					if self._result: self.print_check_result(desc, 'yes', '32')
					else: self.print_check_result(desc, 'no', '31')
			return self._result

	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			sig = Sig()
			e = os.environ.get('PKG_CONFIG_PATH', None)
			if e is not None: sig.update(e)
			sig = self._sig = sig.digest()
			return sig

class BuildCheckTask(Task):
	def __init__(self, name, base_cfg):
		Task.__init__(self, base_cfg.project)
		self.name = name
		self.base_cfg = base_cfg

	def apply_to(self, cfg): pass

	@property
	def source_text(self): return '#error ' + str(self.__class__) + ' did not redefine default source text.\n'

	@property
	def _prog_source_text(self): return self.source_text + '\nint main() { return 0; }\n'

	@property
	def cfg(self):
		try: return self._cfg
		except AttributeError:
			self._cfg = self.base_cfg.clone()
			self.apply_to(self._cfg)
			return self._cfg
	
	@property
	def uid(self): return self.name

	@property
	def bld_dir(self):
		try: return self._bld_dir
		except AttributeError:
			self._bld_dir = self.project.bld_node.node_path('checks').node_path(self.name)
			return self._bld_dir

	def __call__(self, sched_context):
		try: self._result
		except AttributeError:
			sched_context.lock.release()
			try: self.result
			finally: sched_context.lock.acquire()
		raise StopIteration

	@property
	def result(self):
		try: return self._result
		except AttributeError:
			changed = False
			try: old_sig, self._result = self.project.state_and_cache[self.uid]
			except KeyError: changed = True
			else:
				if old_sig != self.sig: changed = True
			if not changed:
				if __debug__ and is_debug: debug('task: skip: no change: ' + self.name)
			else:
				if not silent:
					desc = 'checking for ' + self.name
					self.print_check(desc)
				dir = self.bld_dir
				dir.make_dir(dir.parent)
				r, out, err = self.cfg.impl.process_build_check_task(self)
				log = dir.node_path('build.log')
				f = open(log.path, 'w')
				try:
					f.write(self._prog_source_text); f.write('\n')
					f.write(str(self.cfg.cxx_args)); f.write('\n')
					f.write(str(self.cfg.ld_args)); f.write('\n')
					f.write(out); f.write('\n')
					f.write(err); f.write('\n')
					f.write('return code: '); f.write(str(r)); f.write('\n')
				finally: f.close()
				self._result = r == 0
				self.project.state_and_cache[self.uid] = self.sig, self._result
				if not silent:
					if self._result: self.print_check_result(desc, 'yes', '32')
					else: self.print_check_result(desc, 'no', '31')
			return self._result

	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			sig = Sig(self.source_text)
			sig.update(self.base_cfg.cxx_sig)
			sig.update(self.base_cfg.ld_sig)
			sig = self._sig = sig.digest()
			return sig
