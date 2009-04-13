#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2007-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os, threading
from collections import deque

from logger import out, is_debug, debug, colored, silent
from signature import Sig
from option_cfg import OptionCfg
from fhs import FHS
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
		self.pkg_config = []
		
	def clone(self, class_ = None):
		if class_ is None: class_ = self.__class__
		c = class_(self.project)
		c.defines.update(self.defines)
		c.include_paths.extend(self.include_paths)
		c.cxx_flags += self.cxx_flags
		c.lib_paths.extend(self.lib_paths)
		c.libs += self.libs
		c.static_libs += self.static_libs
		c.shared_libs += self.shared_libs
		c.ld_flags += self.ld_flags
		c.pkg_config += self.pkg_config
		return c
		
class BuildCfg(ClientCfg):
	def __init__(self, project):
		ClientCfg.__init__(self, project)
		self.cxx_prog = None
		self.pic = None
		self.includes = deque()
		self.ld_prog = None
		self.ar_prog = None
		self.ranlib_prog = None
		self.shared = None
		self.static_prog = None
		self.impl = None
		self.kind = self.version = None
		self.debug = False
		self.optim = None
		self.check_missing = False
		self.fhs = FHS(project)

	def clone(self, class_ = None):
		if class_ is None: class_ = self.__class__
		c = ClientCfg.clone(self, class_)
		c.cxx_prog = self.cxx_prog
		c.pic = self.pic
		c.includes.extend(self.includes)
		c.ld_prog = self.ld_prog
		c.ar_prog = self.ar_prog
		c.ranlib_prog = self.ranlib_prog
		c.shared = self.shared
		c.static_prog = self.static_prog
		c.impl = self.impl
		c.kind = self.kind
		c.version = self.version
		c.debug = self.debug
		c.optim = self.optim
		c.check_missing = self.check_missing
		c.fhs = self.fhs
		return c

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
			sig.update(str(self.check_missing))
			if len(self.pkg_config): sig.update(_PkgConfigTask.env_sig())
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
			sig.update(str(self.static_prog))
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
	def cxx_args_cwd(self):
		try: return self._cxx_args_cwd
		except AttributeError:
			args = self._cxx_args_cwd = self.impl.cfg_cxx_args_cwd(self)
			if __debug__ and is_debug: debug('cfg: cxx: build: cxx cwd: ' + str(args))
			return args

	@property
	def cxx_args_bld(self):
		try: return self._cxx_args_bld
		except AttributeError:
			args = self._cxx_args_bld = self.impl.cfg_cxx_args_bld(self)
			if __debug__ and is_debug: debug('cfg: cxx: build: cxx bld: ' + str(args))
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

class UserBuildCfg(BuildCfg, OptionCfg):
	def clone(self, class_ = None):
		if class_ is None: class_ = BuildCfg
		return class_.clone(self, class_)

	known_options = set([
		'cxx',
		'cxx-flags',
		'cxx-debug',
		'cxx-optim',
		'cxx-pic',
		'cxx-mod-shared-libs',
		'cxx-mod-static-progs',
		'cxx-mod-ld',
		'cxx-mod-ld-flags',
		'cxx-mod-ar',
		'cxx-mod-ranlib',
		'check-missing'
	])

	@staticmethod
	def generate_option_help(help):
		help['cxx']                  = ('<prog>', 'use <prog> as c++ compiler')
		help['cxx-flags']            = ('[flags]', 'use specific c++ compiler flags')
		help['cxx-debug']            = ('<yes|no>', 'whether to make the c++ compiler produce debugging information', 'no')
		help['cxx-optim']            = ('<level>', 'use c++ compiler optimisation <level>')
		help['cxx-pic']              = ('<yes|no>', 'whether to make the c++ compiler emit pic code rather than non-pic code for static libs and programs (always pic for shared libs)', 'no (for static libs and programs)')
		#help['cxx-mod-shared']      = ('<yes|no|progs-only>', '...', 'yes')
		#help['cxx-mod-static']      = ('<no|libs|libs-and-progs>', '...', 'no')
		help['cxx-mod-shared-libs']  = ('<yes|no>', 'whether to build shared libs (rather than static libs)', 'yes unless cxx-pic is set explicitly to no or cxx-mod-static-progs is set to yes')
		help['cxx-mod-static-progs'] = ('<yes|no>', 'whether to statically link programs (rather than dynamically using shared libs)', 'no')
		help['cxx-mod-ld']           = ('<prog>', 'use <prog> as shared lib and program linker')
		help['cxx-mod-ld-flags']     = ('[flags]', 'use specific linker flags')
		help['cxx-mod-ar']           = ('<prog>', 'use <prog> as static lib archiver', 'ar')
		help['cxx-mod-ranlib']       = ('<prog>', 'use <prog> as static lib archive indexer', 'ranlib (or via ar s flag for gnu ar)')
		help['check-missing']        = ('<yes|no>', 'check for missing built files (rebuilds files you manually deleted in the build dir)', 'no')

	def __init__(self, project):
		BuildCfg.__init__(self, project)
		OptionCfg.__init__(self, project)
		
		try:
			old_sig, self.check_missing, \
			self.kind, self.version, \
			self.cxx_prog, self.cxx_flags, self.pic, self.optim, self.debug, \
			self.shared, self.static_prog, self.ld_prog, self.ld_flags, \
			self.ar_prog, self.ranlib_prog = \
				self.project.persistent[str(self.__class__)]
		except KeyError: old_sig = None
		if old_sig != self.options_sig:
			if __debug__ and is_debug: debug('cfg: cxx: user: parsing options')
			o = self.options

			if 'check-missing' in o: self.check_missing = o['check-missing'] == 'yes'
			else: self.check_missing = False

			if 'cxx' in o: self.cxx_prog = o['cxx']
			if 'cxx-flags' in o: self.cxx_flags = o['cxx-flags'].split()
			else:
				flags = os.environ.get('CXXFLAGS', None)
				if flags is not None: self.cxx_flags = flags.split()
				else: self.cxx_flags = []

			self.optim = o.get('cxx-optim', None)
			self.debug = o.get('cxx-debug', False)

			if 'cxx-pic' in o: self.pic = o['cxx-pic'] != 'no'
			else: self.pic = None

			if 'cxx-mod-shared-libs' in o: self.shared = o['cxx-mod-shared-libs'] != 'no'
			else: self.shared = None
			
			if 'cxx-mod-static-progs' in o:
				self.static_prog = o['cxx-mod-static-progs'] == 'yes'
				if self.static_prog and self.shared is None: self.shared = False
			else: self.static_prog = False

			if self.pic is None:
				if self.shared is None: self.shared = True
				self.pic = False # this is for programs only
			elif self.shared is None: self.shared = self.pic

			if 'cxx-mod-ld' in o: self.ld_prog = o['cxx-mod-ld']
			if 'cxx-mod-flags' in o: self.cxx_mod_flags = o['cxx-mod-flags'].split()
			else:
				flags = os.environ.get('LDFLAGS', None)
				if flags is not None: self.ld_flags = flags.split()
				else: self.ld_flags = []
			if 'cxx-mod-ar' in o: self.ar_prog = o['cxx-mod-ar']
			if 'cxx-mod-ranlib' in o: self.ranlib_prog = o['cxx-mod-ranlib']

			self._check_compiler()

			if 'cxx-mod-ld' not in o: self.ld_prog = self.impl.ld_prog
			if 'cxx-mod-ar' not in o: self.ar_prog = self.impl.ar_prog
			if 'cxx-mod-ranlib' not in o: self.ranlib_prog = self.impl.ranlib_prog
			
			self.project.persistent[str(self.__class__)] = \
				self.options_sig, self.check_missing, \
				self.kind, self.version, \
				self.cxx_prog, self.cxx_flags, self.pic, self.optim, self.debug, \
				self.shared, self.static_prog, self.ld_prog, self.ld_flags, \
				self.ar_prog, self.ranlib_prog

		elif self.kind == 'gcc':
			import gcc
			self.impl = gcc.Impl()

		if self.impl is None: raise Exception, 'unsupported c++ compiler'

	def _check_compiler(self):
		o = self.options
		if 'cxx' not in o: self.cxx_prog = 'c++'
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
			if 'cxx-mod-ld' not in o: self.ld_prog = self.cxx_prog
			import gcc
			self.impl = gcc.Impl()
		if not silent: self.print_check_result(desc, str(self.kind) + ' version ' + str(self.version), '32')

class _PreCompileTask(Task):
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
			return self._cfg

	def apply_to(self, cfg): cfg.includes.append(self.header)

	def __str__(self): return str(self.header)

	@property
	def uid(self): return self.name

	@property
	def header(self):
		try: return self._header
		except AttributeError:
			self._header = self.project.bld_dir / 'precompiled' / (self.name + '.private.hpp')
			return self._header

	@property
	def target(self):
		try: return self._target
		except AttributeError:
			self._target = self.header.parent / (self.header.name + self.cfg.impl.precompile_task_target_ext)
			return self._target

	@property
	def target_dir(self): return self.target.parent

	def __call__(self, sched_context):
		if len(self.cfg.pkg_config) != 0:
			pkg_config_cxx_flags_task = _PkgConfigCxxFlagsTask(self.project, self.cfg.pkg_config)
			sched_context.parallel_wait((pkg_config_cxx_flags_task,))
			pkg_config_cxx_flags_task.apply_to(self.cfg)
		sched_context.lock.release()
		try:
			changed = False
			try: old_sig, deps, old_dep_sig = self.project.persistent[self.uid]
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
							self.target_dir.lock.acquire()
							try:
								try: self.target_dir.actual_children # not needed, just an optimisation
								except OSError: pass
							finally: self.target_dir.lock.release()
							if not self.target.exists:
								if __debug__ and is_debug: debug('task: target missing: ' + str(self.target))
								changed = True
			if not changed:
				if __debug__ and is_debug: debug('task: skip: no change: ' + str(self.header))
			else:
				if not silent: 
					if self.cfg.pic: pic = 'pic'; color = '7;1;35'
					else: pic = 'non-pic'; color = '7;35'
					self.print_desc('pre-compiling ' + pic + ' c++ ' + str(self), color)
				dir = self.header.parent
				dir.make_dir(dir.parent)
				f = open(self.header.path, 'w')
				try: f.write(self.source_text); f.write('\n')
				finally: f.close()
				self.cfg.impl.process_precompile_task(self, sched_context.lock)
				if False:
					# We create a file with a #error to ensure the pch is used.
					f = open(self.header.path, 'w')
					try: f.write('#error pre-compiled header missed\n');
					finally: f.close()
		finally: sched_context.lock.acquire()

	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			sig = Sig(self.source_text)
			sig.update(self.cfg.cxx_sig)
			sig = self._sig = sig.digest()
			return sig

class PreCompileTasks(Task):
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
			return self._cfg

	@property
	def lib_task(self):
		try: return self._lib_task
		except AttributeError:
			self._create_tasks()
			return self._lib_task

	@property
	def prog_task(self):
		try: return self._prog_task
		except AttributeError:
			self._create_tasks()
			return self._prog_task

	def _create_tasks(self):
		pic_task = non_pic_task = None
		if self.cfg.shared or self.cfg.pic:
			pic_task = PreCompileTasks.OneTask(self, pic = True)
			self._lib_task = pic_task
		else:
			non_pic_task = PreCompileTasks.OneTask(self, pic = False)
			self._lib_task = non_pic_task
		if self.cfg.pic:
			if pic_task is None: pic_task = PreCompileTasks.OneTask(self, pic = True)
			self._prog_task = pic_task
		else:
			if non_pic_task is None: non_pic_task = PreCompileTasks.OneTask(self, pic = False)
			self._prog_task = non_pic_task

	class OneTask(_PreCompileTask):
		def __init__(self, parent_task, pic):
			_PreCompileTask.__init__(self, parent_task.name + (not pic and '-non' or '') + '-pic', parent_task.cfg)
			self.parent_task = parent_task
			self.pic = pic

		@property
		def source_text(self): return self.parent_task.source_text

		def __call__(self, sched_ctx):
			sched_ctx.parallel_wait((self.parent_task,))
			self.cfg.pic = self.pic
			_PreCompileTask.__call__(self, sched_ctx)

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
	def target_dir(self): return self.mod_task.obj_dir

	def __call__(self, sched_context):
		self.target_dir.make_dir()
		self.target_dir.actual_children # not needed, just an optimisation
		sched_context.lock.release()
		try:
			if not silent:
				if self.cfg.pic: pic = 'pic'; color = '7;1;34'
				else: pic = 'non-pic'; color = '7;34'
				self.print_desc('batch-compiling ' + pic + ' objects from c++ ' + str(self), color)
			self._actual_sources = []
			for s in self.sources:
				node = self.target_dir / self.mod_task._unique_base_name(s)
				if not node.exists:
					f = open(node.path, 'w')
					try: f.write('#include "%s"\n' % s.rel_path(self.target_dir))
					finally: f.close()
				self._actual_sources.append(node)
			self.cfg.impl.process_cxx_task(self, sched_context.lock)
		finally: sched_context.lock.acquire()

class ModTask(Task):
	class Kinds(object):
		PROG = 0
		LIB = 1
		LOADABLE = 2

	def __init__(self, name, kind, base_cfg, aliases = None):
		Task.__init__(self, base_cfg.project, aliases or (name,))
		self.name = name
		self.kind = kind
		self.base_cfg = base_cfg
		self.sources = []
		self.dep_lib_tasks = []

	@property
	def ld(self):
		try: return self._ld
		except AttributeError:
			if self.kind == ModTask.Kinds.PROG: self._ld = True
			else: self._ld = self.cfg.shared
			return self._ld

	@property
	def cfg(self):
		try: return self._cfg
		except AttributeError:
			cfg = self._cfg = self.base_cfg.clone()
			if self.kind == ModTask.Kinds.PROG: cfg.shared = False
			else:
				if self.kind == ModTask.Kinds.LOADABLE: cfg.shared = True
				if cfg.shared and not cfg.pic:
					debug('cfg: cxx: mod: shared lib => overriding cfg to pic')
					cfg.pic = True
			return cfg

	def __str__(self): return str(self.target)

	@property
	def uid(self): return self.name

	@property
	def target(self):
		try: return self._target
		except AttributeError:
			self._target = self.cfg.impl.mod_task_target_dir(self) / self.cfg.impl.mod_task_target_name(self)
			return self._target

	@property
	def obj_dir(self):
		try: return self._obj_dir
		except AttributeError:
			self._obj_dir = self.project.bld_dir / 'modules' / self.name
			return self._obj_dir

	@property
	def target_dir(self): return self.target.parent

	def __call__(self, sched_context):
		if len(self.dep_lib_tasks) != 0: sched_context.parallel_no_wait(self.dep_lib_tasks)
		if len(self.cfg.pkg_config) != 0:
			pkg_config_cxx_flags_task = _PkgConfigCxxFlagsTask(self.project, self.cfg.pkg_config)
			sched_context.parallel_wait((pkg_config_cxx_flags_task,))
			pkg_config_cxx_flags_task.apply_to(self.cfg)
			if self.ld:
				pkg_config_ld_flags_task = _PkgConfigLdFlagsTask(self.project, self.cfg.pkg_config, self.cfg.shared or not self.cfg.static_prog)
				sched_context.parallel_no_wait((pkg_config_ld_flags_task,))
		changed_sources = []
		try: state = self.project.persistent[self.uid]
		except KeyError:
			if __debug__ and is_debug: debug('task: no state: ' + str(self))
			state = self.project.persistent[self.uid] = None, None, None, {}
			self._type_changed = False
			changed_sources = self.sources
		else:
			self._type_changed = state[1] != self.ld
			if __debug__ and is_debug and self._type_changed: debug('task: mod type changed: ' + str(self))
			if state[2] != self.cfg.cxx_sig:
				if __debug__ and is_debug: debug('task: cxx sig changed: ' + str(self))
				changed_sources = self.sources
			else:
				implicit_deps = state[3]
				for s in self.sources:
					try: deps, old_dep_sig = implicit_deps[s] # TODO also put self.cfg.cxx_sig, and -include in implicit_deps
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
						self.target_dir.lock.acquire()
						try:
							try: self.target_dir.actual_children # not needed, just an optimisation
							except OSError: pass
						finally: self.target_dir.lock.release()
						o = self.obj_dir / self._obj_name(s)
						if not o.exists:
							if __debug__ and is_debug: debug('task: target missing: ' + str(o))
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
			sched_context.parallel_wait(tasks)
		elif self.cfg.check_missing and not self.target.exists:
			if __debug__ and is_debug: debug('task: target missing: ' + str(self))
			changed_sources = self.sources
			need_process = True
		if self.ld:
			if len(self.cfg.pkg_config) != 0:
				sched_context.wait((pkg_config_ld_flags_task,))
				pkg_config_ld_flags_task.apply_to(self.cfg)
			if len(self.dep_lib_tasks) != 0:
				sched_context.wait(self.dep_lib_tasks)
				for l in self.dep_lib_tasks:
					self.cfg.lib_paths.append(l.target.parent)
					self.cfg.libs.append(l.name)
		if not need_process:
			if state[0] != self._mod_sig:
				if __debug__ and is_debug: debug('task: mod sig changed: ' + str(self))
				changed_sources = self.sources
				need_process = True
			else:
				for t in self.dep_lib_tasks:
					# when a dependant lib is a static archive, or changes its type from static to shared, we need to relink.
					# when the check-missing option is on, we also relink to check that external symbols still exist.
					try: need_process = t._needed_process and (not t.ld or t._type_changed or self.cfg.check_missing)
					except AttributeError: continue # not a lib task
					if need_process:
						if __debug__ and is_debug: debug('task: in lib task changed: ' + str(self) + ' ' + str(t))
						break
		if not need_process:
			if __debug__ and is_debug: debug('task: skip: no change: ' + str(self))
		else:
			self.target_dir.make_dir()
			sched_context.lock.release()
			try:
				if not silent:
					if not self.ld: desc = 'archiving and indexing static lib'; color = '7;36'
					elif self.kind == ModTask.Kinds.PROG:
						if self.cfg.pic: pic = 'pic'; color = '1;7'
						else: pic = 'non-pic'; color = '7'
						if self.cfg.static_prog: shared = 'static'; color += ';37;40'
						else: shared = 'dynamic'; color += ';32'
						desc = 'linking ' + shared + ' ' + pic + ' program'
					elif self.kind == ModTask.Kinds.LOADABLE: desc = 'linking loadable module'; color = '1;7;34'
					else: desc = 'linking shared lib'; color = '1;7;33'
					self.print_desc(desc + ' ' + str(self), color)
				if self.ld: sources = self.sources
				else: sources = changed_sources
				self.cfg.impl.process_mod_task(self, [self._obj_name(s) for s in sources])
				implicit_deps = self.project.persistent[self.uid][3]
				if len(implicit_deps) > len(self.sources):
					# remove old sources from implicit deps dictionary
					sources_states = {}
					for s in self.sources: sources_states[s] = implicit_deps[s]
				else: sources_states = implicit_deps
				self.project.persistent[self.uid] = self._mod_sig, self.ld, self.cfg.cxx_sig, sources_states # TODO move cxx_sig into obj sig
			finally: sched_context.lock.acquire()
		if not self.cfg.check_missing: self.obj_dir.forget()
		self._needed_process = need_process

	def _unique_base_name(self, source):
		return source.rel_path(self.project.top_src_dir).replace(os.pardir, '_').replace(os.sep, ',')

	def _obj_name(self, source):
		name = self._unique_base_name(source)
		return name[:name.rfind('.')] + self.cfg.impl.cxx_task_target_ext

	@property
	def _mod_sig(self):
		try: return self.__mod_sig
		except AttributeError:
			sig = Sig(self.target_dir.abs_path)
			if self.ld: sig.update(self.cfg.ld_sig)
			else: sig.update(self.cfg.ar_ranlib_sig)
			self.__mod_sig = sig = sig.digest()
			return sig

class _PkgConfigTask(Task):
	def __init__(self, project, pkgs):
		Task.__init__(self, project)
		self.pkgs = pkgs

	@property
	def prog(self): return 'pkg-config'

	@property
	def desc(self):
		try: return self._desc
		except AttributeError:
			self._desc = 'checking for ' + self.prog + ' ' + ' '.join(self.pkgs) + ' ' + self.what_desc
			return self._desc

	@property
	def what_desc(self): raise Exception, str(self.__class__) + ' did not redefine the property.'
	
	@property
	def what_args(self): raise Exception, str(self.__class__) + ' did not redefine the property.'

	def apply_to(self): raise Exception, str(self.__class__) + ' did not redefine the method.'

	@property
	def args(self): return [self.prog] + self.pkgs + self.what_args

	def __str__(self): return ' '.join(self.pkgs) + ' ' + ' '.join(self.what_args)

	@property
	def uid(self):
		try: return self._uid
		except AttributeError:
			pkgs = self.pkgs
			pkgs.sort()
			self._uid = ' '.join(pkgs) + ' '.join(self.what_args) #XXX
			return self._uid

	def __call__(self, sched_context):
		try: self._result
		except AttributeError:
			sched_context.lock.release()
			try: self.result
			finally: sched_context.lock.acquire()

	@property
	def result(self):
		try: return self._result
		except AttributeError:
			changed = False
			try: old_sig, self._result = self.project.persistent[self.uid]
			except KeyError: changed = True
			else:
				if old_sig != self.sig: changed = True
			if not changed:
				if __debug__ and is_debug: debug('task: skip: no change: ' + str(self))
			else:
				if not silent: self.print_check(self.desc)
				self.do_result()
				self.project.persistent[self.uid] = self.sig, self._result
			return self._result

	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			sig = Sig(_PkgConfigTask.env_sig())
			pkgs = self.pkgs
			pkgs.sort()
			for p in pkgs: sig.update(p)
			sig = self._sig = sig.digest()
			return sig

	@staticmethod
	def env_sig():
		sig = Sig()
		for name in ('PKG_CONFIG_PATH', 'PKG_CONFIG_LIBDIR', 'PKG_CONFIG_DISABLE_UNINSTALLED'): # PKG_CONFIG_TOP_BUILD_DIR, PKG_CONFIG_ALLOW_SYSTEM_CFLAGS, PKG_CONFIG_ALLOW_SYSTEM_LIBS
			e = os.environ.get(name, None)
			if e is not None: sig.update(e)
		return sig.digest()

class PkgConfigCheckTask(_PkgConfigTask):
	@property
	def what_desc(self): return 'existence'
	
	@property
	def what_args(self): return ['--exists']

	def apply_to(self, cfg): cfg.pkg_config += self.pkgs
	
	def do_result(self):
		self._result = 0 == exec_subprocess(self.args)
		if not silent:
			if self._result: self.print_check_result(self.desc, 'yes', '32')
			else: self.print_check_result(self.desc, 'no', '31')

class _PkgConfigFlagsTask(_PkgConfigTask):
	def do_result(self):
			r, out, err = exec_subprocess_pipe(self.args, silent = True)
			if r != 0: raise Exception, r
			if not silent: self.print_check_result(self.desc, out.rstrip('\n'), '32')
			self._result = out.split()

class _PkgConfigCxxFlagsTask(_PkgConfigFlagsTask):
	@property
	def what_desc(self): return 'cxx flags'
	
	@property
	def what_args(self): return ['--cflags']

	def apply_to(self, cfg): cfg.cxx_flags += self.result

class _PkgConfigLdFlagsTask(_PkgConfigFlagsTask):
	def __init__(self, project, pkgs, shared):
		_PkgConfigFlagsTask.__init__(self, project, pkgs)
		self.shared = shared

	@property
	def what_desc(self):
		if self.shared: return 'shared ld flags'
		else: return 'static ld flags'
	
	@property
	def what_args(self):
		if self.shared: return ['--libs']
		else: return ['--libs', '--static']

	def apply_to(self, cfg): cfg.ld_flags += self.result

class BuildCheckTask(Task):
	def __init__(self, name, base_cfg):
		Task.__init__(self, base_cfg.project)
		self.name = name
		self.base_cfg = base_cfg

	def __str__(self): return self.name

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
			self._bld_dir = self.project.bld_dir / 'checks' / self.name
			return self._bld_dir

	def __call__(self, sched_context):
		try: self._result
		except AttributeError:
			sched_context.lock.release()
			try: self.result
			finally: sched_context.lock.acquire()

	@property
	def result(self):
		try: return self._result
		except AttributeError:
			changed = False
			try: old_sig, self._result = self.project.persistent[self.uid]
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
				log = dir / 'build.log'
				f = open(log.path, 'w')
				try:
					f.write(self._prog_source_text); f.write('\n')
					f.write(str(self.cfg.cxx_args_cwd)); f.write('\n')
					f.write(str(self.cfg.ld_args)); f.write('\n')
					f.write(out); f.write('\n')
					f.write(err); f.write('\n')
					f.write('return code: '); f.write(str(r)); f.write('\n')
				finally: f.close()
				self._result = r == 0
				self.project.persistent[self.uid] = self.sig, self._result
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
