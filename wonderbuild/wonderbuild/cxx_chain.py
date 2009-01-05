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

class UserCfg(Cfg):
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
	
	def configure(self):
		try:
			old_sig, self.check_missing, \
			self.kind, self.version, \
			self.cxx_prog, self.cxx_flags, self.pic, self.optim, self.debug, \
			self.shared, self.ld_prog, self.ld_flags, \
			self.ar_prog, self.ar_flags, self.ranlib_prog, self.ranlib_flags, \
			self._cxx_args, self._mod_args = \
				self.project.state_and_cache[self.__class__.__name__]
		except KeyError: parse = True
		else: parse = old_sig != self.sig

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
				import gcc
				self.impl = gcc.Impl()
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
			self.ar_flags = 'rc'
			if self.kind == 'gcc': self.ar_flags += 's'
				
			if not ranlib_prog: self.ranlib_prog = self.impl.ranlib_prog
			self.ranlib_flags = None
			
			self.project.state_and_cache[self.__class__.__name__] = \
				self.sig, self.check_missing, \
				self.kind, self.version, \
				self.cxx_prog, self.cxx_flags, self.pic, self.optim, self.debug, \
				self.shared, self.ld_prog, self.ld_flags, \
				self.ar_prog, self.ar_flags, self.ranlib_prog, self.ranlib_flags, \
				self.cxx_args, self.mod_args

		elif self.kind == 'gcc':
			import gcc
			self.impl = gcc.Impl()

		if self.impl is None:
			raise Exception, 'unsupported c++ compiler'

	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			sig = Sig(self.env_sig)
			sig.update(self.options_sig) # TODO don't sign the options, because we miss the defaults
			sig = self._sig = sig.digest()
			return sig

	@property
	def env_sig(self):
		try: return self._env_sig
		except AttributeError:
			sig = Sig()
			e = os.environ.get('PATH', None)
			if e is not None: sig.update(e)
			sig = self._env_sig = sig.digest()
			return sig

	@property
	def cxx_options_sig(self):
		try: return self._cxx_options_sig
		except AttributeError:
			sig = Sig()
			for o in options:
				for oo in self.__class__._cxx_options:
					if o.startswith(oo + '='): sig.update(o)
			sig = self._cxx_options_sig = sig.digest()
			return sig

	@property
	def mod_options_sig(self):
		try: return self._mod_options_sig
		except AttributeError:
			sig = Sig()
			for o in options:
				for oo in self.__class__._mod_options:
					if o.startswith(oo + '='): sig.update(o)
			sig = self._mod_options_sig = sig.digest()
			return sig

	@property
	def cxx_sig(self):
		try: return self._cxx_sig
		except AttributeError:
			sig = Sig(self.cxx_options_sig) # TODO don't sign the options, because we miss the defaults
			sig.update(self.env_sig) # TODO sign abs prog paths instead
			sig.update(self.impl.cxx_env_sig)
			sig = self._cxx_sig = sig.digest()
			return sig

	@property
	def mod_sig(self):
		try: return self._mod_sig
		except AttributeError:
			sig = Sig(self.mod_options_sig) # TODO don't sign the options, because we miss the defaults
			sig.update(self.env_sig) # TODO sign abs prog paths instead
			sig.update(self.impl.mod_env_sig)
			sig = self._mod_sig = sig.digest()
			return sig

	@property
	def cxx_args(self):
		try: return self._cxx_args
		except AttributeError:
			args = self._cxx_args = self.impl.user_cfg_cxx_args(self)
			if __debug__ and is_debug: debug('cfg: cxx: user: cxx: ' + str(args))
			return args

	@property
	def mod_args(self):
		try: return self._mod_args
		except AttributeError:
			args = self._mod_args = self.impl.user_cfg_mod_args(self)
			if __debug__ and is_debug: debug('cfg: cxx: user: mod: ' + str(args))
			return args

class DevCfg(Cfg):
	def __init__(self, user_cfg, kind):
		Cfg.__init__(self, user_cfg.project)
		self.user_cfg = user_cfg
		self.kind = kind

	@property
	def impl(self): return self.user_cfg.impl
	
	def configure(self):
		self.pkgs = []
		self.include_paths = []
		self.defines = {}
		self.pic = self.user_cfg.pic
		if self.kind == 'prog':
			self.shared = False
			self.ld = True
		else:
			self.shared = self.ld = self.user_cfg.shared
			if self.shared and not self.pic:
				debug('cfg: cxx: dev: shared lib => overriding cfg to pic')
				self.pic = True
		self.libs_paths = []
		self.libs = []
		self.static_libs = []
		self.shared_libs = []

	@property
	def cxx_sig(self):
		try: return self._cxx_sig
		except AttributeError:
			sig = Sig(self.user_cfg.cxx_sig)
			sig.update(str(self.pic))
			for k, v in self.defines.iteritems():
				sig.update(k)
				if v is not None: sig.update(v)
			for p in self.include_paths: sig.update(p.path)
			for p in self.pkgs: sig.update(p.sig)
			sig = self._cxx_sig = sig.digest()
			return sig

	@property
	def mod_sig(self):
		try: return self._mod_sig
		except AttributeError:
			sig = Sig(self.user_cfg.mod_sig)
			sig.update(str(self.shared))
			for p in self.libs_paths: sig.update(p.path)
			for l in self.libs: sig.update(l)
			for l in self.static_libs: sig.update(l)
			for l in self.shared_libs: sig.update(l)
			for p in self.pkgs: sig.update(p.sig)
			sig = self._mod_sig = sig.digest()
			return sig

	@property
	def cxx_args(self):
		self.lock.acquire()
		try:
			try: return self._cxx_args
			except AttributeError:
				args = self.user_cfg.cxx_args[:]
				self.impl.dev_cfg_cxx_args(self, args)
				for p in self.pkgs: args += p.cxx_args
				if __debug__ and is_debug: debug('cfg: cxx: dev: cxx: ' + str(args))
				self._cxx_args = args
				return args
		finally: self.lock.release()

	@property
	def mod_args(self):
		self.lock.acquire()
		try:
			try: return self._mod_args
			except AttributeError:
				ld_args, ar_args, ranlib_args = self.user_cfg.mod_args
				if not self.ld: args = ar_args, ranlib_args
				else:
					args = ld_args[:]
					self.impl.dev_cfg_ld_args(self, args)
					for p in self.pkgs: args += p.mod_args
				if __debug__ and is_debug: debug('cfg: cxx: dev: mod: ' + str(args))
				self._mod_args = args
				return args
		finally: self.lock.release()

class CxxTask(Task):
	def __init__(self, mod_task):
		Task.__init__(self, mod_task.project)
		self.mod_task = mod_task
		self.sources = []

	@property
	def cfg(self): return self.mod_task.cfg

	@property
	def user_cfg(self): return self.cfg.user_cfg
	
	@property
	def impl(self): return self.user_cfg.impl

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
		self.impl.process_cxx_task(self)
		Task.process(self)

class ModTask(Task):
	def __init__(self, dev_cfg, name, aliases = None):
		Task.__init__(self, dev_cfg.project, aliases)
		self.cfg = dev_cfg
		self.name = name
		self.sources = []

	@property
	def user_cfg(self): return self.cfg.user_cfg
	
	@property
	def impl(self): return self.user_cfg.impl

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
				node_path(self.impl.mod_task_target_name(self))
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
					if self.user_cfg.check_missing:
						o = self.target_dir.node_path(self._obj_name(s))
						if not o.exists:
							if __debug__ and is_debug: debug('task: target removed: ' + str(o))
							changed_sources.append(s)
							continue
					if __debug__ and is_debug: debug('task: skip: no change: ' + str(s))
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
		if self.user_cfg.check_missing and not self.target.exists:
			if __debug__ and is_debug: debug('task: target removed: ' + str(self))
			self._changed_sources = self.sources
			return True
		if len(self._changed_sources) != 0: return True
		state = self.project.task_states[self.uid]
		if state[0] != self.cfg.mod_sig:
			if __debug__ and is_debug: debug('task: mod sig changed: ' + str(self))
			self._changed_sources = self.sources
			return True
		for t in self.in_tasks:
			if t.processed:
				try: ld = t.cfg.ld
				except AttributeError: continue # not a lib task
				if not ld:
					if __debug__ and is_debug: debug('task: in task changed: ' + str(self) + ' ' + str(t))
					return True
		if __debug__ and is_debug: debug('task: skip: no change: ' + str(self))
		return False

	def process(self):
		if not silent:
			if not self.cfg.ld: desc = 'archiving and indexing static lib'; color = '7;36'
			elif self.cfg.kind == 'prog':
				if not self.cfg.pic: desc = 'linking non-pic program'; color = '7;32'
				else: desc = 'linking pic program'; color = '7;1;32'
			elif self.cfg.kind == 'loadable': desc = 'linking loadable module'; color = '7;1;34'
			else: desc = 'linking shared lib'; color = '7;1;33'
			self.print_desc(desc + ' ' + str(self), color)
		if self.cfg.ld: sources = self.sources
		else: sources = self._changed_sources
		self.impl.process_mod_task(self, [self._obj_name(s) for s in sources])
		implicit_deps = self.project.task_states[self.uid][2]
		# remove old sources from implicit deps dictionary
		sources_states = {}
		for s in self.sources: sources_states[s] = implicit_deps[s]
		self.project.task_states[self.uid] = self.cfg.mod_sig, self.cfg.cxx_sig, sources_states
		Task.process(self)

	def _unique_base_name(self, source):
		return source.rel_path(self.project.src_node).replace(os.pardir, '_').replace(os.sep, ',')

	def _obj_name(self, source):
		name = self._unique_base_name(source)
		return name[:name.rfind('.')] + self.impl.cxx_task_target_ext

class PkgCfg(Cfg):
	def __init__(self, project):
		Cfg.__init__(self, project)
		self.prog = 'pkg-config'
		self.pkgs = []
		self.flags = []

	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			sig = Sig(self.prog)
			e = os.environ.get('PKG_CONFIG_PATH', None)
			if e is not None: sig.update(e)
			for f in self.flags: sig.update(f)
			for p in self.pkgs: sig.update(p)
			sig = self._sig = sig.digest()
			return sig

	@property
	def cxx_args(self):
		self.lock.acquire()
		try:
			try: return self._cxx_args
			except AttributeError:
				args = [self.prog, '--cflags'] + self.flags + self.pkgs
				if not silent: self.print_desc('getting pkg-config compile flags: ' + ' '.join(self.pkgs))
				r, out, err = exec_subprocess_pipe(args, silent = True)
				if r != 0: 
					self.print_result_desc('error\n', color = '31')
					raise Exception, r
				self.print_result_desc('ok\n', color = '32')
				out = out.rstrip('\n').split()
				self._cxx_args = out
				return out
		finally: self.lock.release()

	@property
	def mod_args(self, static = False):
		self.lock.acquire()
		try:
			try: return self._mod_args
			except AttributeError:
				args = [self.prog, '--libs'] + self.flags + self.pkgs
				if static:
					args.append('--static')
					if not silent: self.print_desc('getting pkg-config static libs: ' + ' '.join(self.pkgs))
				elif not silent: self.print_desc('getting pkg-config shared libs: ' + ' '.join(self.pkgs))
				r, out, err = exec_subprocess_pipe(args, silent = True)
				if r != 0: 
					if not silent: self.print_result_desc('error\n', color = '31')
					raise Exception, r
				if not silent: self.print_result_desc('ok\n', color = '32')
				out = out.rstrip('\n').split()
				self._mod_args = out
				return out
		finally: self.lock.release()
