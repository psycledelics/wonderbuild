#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2007-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os, threading
from collections import deque

from wonderbuild import UserReadableException
from wonderbuild.logger import out, is_debug, debug, colored, color_bg_fg_rgb, silent
from wonderbuild.signature import Sig
from wonderbuild.option_cfg import OptionCfg
from wonderbuild.fhs import FHS
from wonderbuild.task import Task, ProjectTask
from wonderbuild.check_task import CheckTask
from wonderbuild.subprocess_wrapper import exec_subprocess, exec_subprocess_pipe

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
		self._applied = set()
		
	def clone(self, class_ = None):
		if class_ is None: class_ = self.__class__
		if __debug__ and is_debug: debug('cfg: clone: ' + str(class_))
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
	
	def apply_to(self, cfg):
		if self in cfg._applied: return
		cfg.defines.update(self.defines)
		cfg.include_paths.extend(self.include_paths)
		cfg.cxx_flags += self.cxx_flags
		cfg.lib_paths.extend(self.lib_paths)
		cfg.libs += self.libs
		cfg.static_libs += self.static_libs
		cfg.shared_libs += self.shared_libs
		cfg.ld_flags += self.ld_flags
		cfg.pkg_config += self.pkg_config
		
class BuildCfg(ClientCfg, Task):
	def __init__(self, project):
		ClientCfg.__init__(self, project)
		Task.__init__(self)
		self.lang = 'c++'
		self.cxx_prog = self.ld_prog = self.ar_prog = self.ranlib_prog = None
		self.pic = self.shared = self.static_prog = None
		self.includes = deque()
		self.pch = None
		self.check_missing = False
		self.fhs = FHS.shared(project)
		self.impl = self.kind = self.version = None
		# following two used only in the impl, so could be moved there
		self.target_platform_binary_format_is_pe = None
		self.pic_flag_defines_pic = None

	def clone(self, class_ = None):
		if class_ is None: class_ = self.__class__
		c = ClientCfg.clone(self, class_)
		c.lang = self.lang
		c.cxx_prog = self.cxx_prog
		c.pic = self.pic
		c.pch = self.pch
		c.includes.extend(self.includes)
		c.ld_prog = self.ld_prog
		c.ar_prog = self.ar_prog
		c.ranlib_prog = self.ranlib_prog
		c.shared = self.shared
		c.static_prog = self.static_prog
		c.check_missing = self.check_missing
		c.fhs = self.fhs
		c.impl = self.impl
		c.kind = self.kind
		c.version = self.version
		c.target_platform_binary_format_is_pe = self.target_platform_binary_format_is_pe
		c.pic_flag_defines_pic = self.pic_flag_defines_pic
		return c

	@property
	def _common_sig(self):
		try: return self.__common_sig
		except AttributeError:
			sig = Sig(self.impl.common_env_sig)
			e = os.environ.get('PATH', None)
			if e is not None: sig.update(e)
			#sig.update(str(self.target_platform_binary_format_is_pe))
			#sig.update(str(self.pic_flag_defines_pic))
			sig.update(self.kind)
			sig.update(str(self.version))
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
			for k in sorted(self.defines.iterkeys()):
				sig.update(k)
				v = self.defines[k]
				if v is not None: sig.update(v)
			for p in self.include_paths: sig.update(p.abs_path)
			if self.pch is not None: sig.update(self.pch.abs_path)
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
			for p in self.lib_paths: sig.update(p.abs_path)
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
			if self.ranlib_prog is not None: sig.update(self.ranlib_prog)
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

	def bld_rel_path(self, node):
		path = node.rel_path(self.project.bld_dir)
		if not os.path.isabs(path): path = os.path.join(os.pardir, os.pardir, path)
		return path

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

class UserBuildCfgTask(BuildCfg, OptionCfg):
	def clone(self, class_ = None):
		if class_ is None: class_ = BuildCfg
		return class_.clone(self, class_)

	known_options = set([
		'check-missing',
		'cxx',
		'cxx-flags',
		'ld',
		'ld-flags',
		'ar',
		'ranlib',
		'static',
		'pic-static'
	])

	@staticmethod
	def generate_option_help(help):
		help['check-missing'] = (None, 'check for missing built files (rebuilds files you manually deleted in the build dir)')

		help['cxx']           = ('<prog>', 'use <prog> as c++ compiler')
		help['cxx-flags']     = ('[flags]', 'use specific c++ compiler flags')
		help['ld']            = ('<prog>', 'use <prog> as shared lib and program linker')
		help['ld-flags']      = ('[flags]', 'use specific linker flags')
		help['ar']            = ('<prog>', 'use <prog> as static lib archiver', 'ar')
		help['ranlib']        = ('<prog>', 'use <prog> as static lib archive indexer', 'the posix ar s flag is used instead')
		
		help['static'] = ('<libs|full>',
			'libs: build libs as static archives (rather than dynamic, shared libs),\n'
			'full: like libs but also statically link programs (rather than dynamically using shared libs)',
			'libs')
		help['pic-static'] = (None,
			'instruct the c++ compiler to emit pic code even for static libs and programs\n' \
			'(shared libs are always pic regardless of this option)', 'non-pic for static libs and programs')

		# posix compiler options -O -g -s
		#help['optim']        = ('<0|1|n>', '...', '0')
		#help['debug']        = ('<yes|no>', '...', 'no')
		#help['strip']        = ('<yes|no>', '...', 'no')

	@staticmethod
	def shared(project):
		try: build_cfg_task = project.cxx_user_build_cfg_task
		except AttributeError: build_cfg_task = project.cxx_user_build_cfg_task = UserBuildCfgTask(project)
		return build_cfg_task
	
	def new_or_clone(self):
		try: build_cfg = self.project.cxx_user_build_cfg
		except AttributeError: build_cfg = self.project.cxx_user_build_cfg = self
		else: build_cfg = build_cfg.clone()
		return build_cfg
	
	def __init__(self, project):
		BuildCfg.__init__(self, project)
		OptionCfg.__init__(self, project)
		
	def __call__(self, sched_ctx):
		o = self.options
		try:
			old_sig, self.check_missing, \
			self.cxx_prog, self.cxx_flags, self.pic, \
			self.shared, self.static_prog, self.ld_prog, self.ld_flags, \
			self.ar_prog, self.ranlib_prog = \
				self.project.persistent[str(self.__class__)]
		except KeyError: old_sig = None
		if old_sig != self.options_sig:
			if __debug__ and is_debug: debug('cfg: cxx: user: parsing options')

			self.check_missing = 'check-missing' in o

			if 'cxx' in o: self.cxx_prog = o['cxx']
			if 'cxx-flags' in o: self.cxx_flags = o['cxx-flags'].split()
			else:
				flags = os.environ.get('CXXFLAGS', None)
				if flags is not None: self.cxx_flags = flags.split()
				else: self.cxx_flags = []

			static = o.get('static', None)
			self.shared = static is None
			self.static_prog = static == 'full'
			
			self.pic = 'pic-static' in o # this is for programs and static libs only
			
			if 'ld' in o: self.ld_prog = o['ld']
			if 'ld-flags' in o: self.ld_flags = o['ld-flags'].split()
			else:
				flags = os.environ.get('LDFLAGS', None)
				if flags is not None: self.ld_flags = flags.split()
				else: self.ld_flags = []
			if 'ar' in o: self.ar_prog = o['ar']
			if 'ranlib' in o: self.ranlib_prog = o['ranlib']

			self.project.persistent[str(self.__class__)] = \
				self.options_sig, self.check_missing, \
				self.cxx_prog, self.cxx_flags, self.pic, \
				self.shared, self.static_prog, self.ld_prog, self.ld_flags, \
				self.ar_prog, self.ranlib_prog

		if True or 'help' not in o: # XXX needs to be done because check tasks need the cfg impl sig
			from detect_impl import DetectImplCheckTask
			detect_impl = DetectImplCheckTask.shared(self)
			for x in sched_ctx.parallel_wait(detect_impl): yield x
			if self.impl is None: raise UserReadableException, 'no supported c++ compiler found'

class ModDepPhases(object):
	def __init__(self):
		self.private_deps = [] # of ModDepPhases
		self.public_deps = [] # of ModDepPhases
		self.cxx_phase = self.mod_phase = None

	@property
	def expose_private_deep_deps(self): return False

	@property
	def all_deps(self): return self.public_deps + self.private_deps

	def __call__(self, sched_ctx):
		### needs changes in CheckTask
		#self.result = True
		#for x in self.do_check_phase(sched_ctx): yield x
		#if self.result and len(self.all_deps) != 0:
			for x in sched_ctx.parallel_wait(*self.all_deps): yield x
			#self.result = min(bool(dep) for dep in self.all_deps)	

	def _get_result(self):
		try: return self._result
		except AttributeError: raise Exception, 'did you forget to process the ' + str(self) + ' task?'
	def _set_result(self, value): self._result = value
	result = property(_get_result, _set_result)
	def __bool__(self): return self.result
	def __nonzero__(self): return self.__bool__() # __bool__ has become the default in python 3

	def do_ensure_deps(self): 
		for dep in self.all_deps:
			if not dep: raise UserReadableException, str(self) + ' requires the following dep: ' + str(dep)
	
	def _applied(self, cfg, what):
		uid = str(id(self)) + '#' + what
		result = uid in cfg._applied
		cfg._applied.add(uid)

	def apply_cxx_to(self, cfg): return not self._applied(cfg, 'cxx')
	def apply_mod_to(self, cfg): return not self._applied(cfg, 'mod')
	
	def do_deps_cxx_phases(self, sched_ctx):
		deps = self.topologically_sorted_unique_deep_deps(expose_private_deep_deps=False)
		cxx_phases = [dep.cxx_phase for dep in deps if dep.cxx_phase is not None]
		for x in sched_ctx.parallel_wait(*cxx_phases): yield x
		for dep in deps: dep.apply_cxx_to(self.cfg) # ordering matters for sig

	def topologically_sorted_unique_deep_deps(self, expose_private_deep_deps):
		try: return \
			expose_private_deep_deps is None and self._private_cut_topologically_sorted_unique_deep_deps or \
			expose_private_deep_deps and self._private_topologically_sorted_unique_deep_deps or \
			self._public_topologically_sorted_unique_deep_deps
		except AttributeError:
			result = deque(); seen = set() # ordering matters for sig, and static libs must appear after their clients
			self._topologically_sorted_unique_deep_deps(result, seen, True, True, expose_private_deep_deps)
			if expose_private_deep_deps is None: self._private_cut_topologically_sorted_unique_deep_deps = result
			elif expose_private_deep_deps: self._private_topologically_sorted_unique_deep_deps = result
			else: self._public_topologically_sorted_unique_deep_deps = result
			return result

	def _topologically_sorted_unique_deep_deps(self, result, seen, root, expose_private_deps, expose_private_deep_deps):
		if not root:
			if self in seen: return
			seen.add(self)
		for dep in expose_private_deps and self.all_deps or self.public_deps:
			if expose_private_deep_deps is None: dep._topologically_sorted_unique_deep_deps(result, seen, False,
				dep.expose_private_deep_deps, dep.expose_private_deep_deps and None)
			else: dep._topologically_sorted_unique_deep_deps(result, seen, False, expose_private_deep_deps, expose_private_deep_deps)
		if not root: result.appendleft(self)

class _PreCompileTask(ModDepPhases, ProjectTask):
	def __init__(self, name, base_cfg):
		ModDepPhases.__init__(self)
		ProjectTask.__init__(self, base_cfg.project)
		self.name = name
		self.base_cfg = base_cfg

	@property
	def cfg(self):
		try: return self._cfg
		except AttributeError:
			self._cfg = self.base_cfg.clone()
			return self._cfg

	def __call__(self, sched_ctx):
		for x in ModDepPhases.__call__(self, sched_ctx): yield x
		self.cxx_phase = _PreCompileTask._CxxPhaseCallbackTask(self)
	
	def apply_cxx_to(self, cfg):
		if not ModDepPhases.apply_cxx_to(self, cfg): return
		cfg.pch = self.header

	@property
	def source_text(self): return '#error ' + str(self.__class__) + ' did not redefine default source text.\n'

	def __str__(self): return 'deps of pre-compilation of ' + str(self.header)

	@property
	def uid(self): return self.name

	@property
	def header(self):
		try: return self._header
		except AttributeError:
			self.project.bld_dir.lock.acquire()
			try: self._header = self.project.bld_dir / 'pre-compiled' / self.name / (self.name + '.private.hpp') # TODO .h for C
			finally: self.project.bld_dir.lock.release()
			return self._header

	@property
	def target(self):
		try: return self._target
		except AttributeError:
			self._target = self.header.parent / self.cfg.impl.precompile_task_target_name(self.header.name)
			return self._target

	@property
	def target_dir(self): return self.target.parent

	class _CxxPhaseCallbackTask(Task):
		def __init__(self, pre_compile_task):
			Task.__init__(self)
			self.pre_compile_task = pre_compile_task
		
		def __str__(self): return 'pre-compile ' + str(self.pre_compile_task.header)
		def __call__(self, sched_ctx):
			for x in self.pre_compile_task._cxx_phase_callback(sched_ctx): yield x

	def do_cxx_phase(self): pass

	def _cxx_phase_callback(self, sched_ctx):
		for x in sched_ctx.parallel_wait(self): yield x
		self.do_ensure_deps()
		for x in self.do_deps_cxx_phases(sched_ctx): yield x
		self.do_cxx_phase()
		if len(self.cfg.pkg_config) != 0:
			self.cfg.cxx_sig # compute the signature before, because we don't need pkg-config cxx flags in the cfg sig
			pkg_config_cxx_flags_task = _PkgConfigCxxFlagsTask.shared(self.project, self.cfg.pkg_config)
			for x in sched_ctx.parallel_wait(pkg_config_cxx_flags_task): yield x
			pkg_config_cxx_flags_task.apply_to(self.cfg)
		sched_ctx.lock.release()
		try:
			changed = False
			try: old_sig, deps, old_dep_sig = self.persistent
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
					self.print_desc('pre-compiling ' + pic + ' c++ ' + str(self.header), color)
				dir = self.header.parent
				dir.make_dir(dir.parent)
				f = open(self.header.path, 'w')
				try: f.write(self.source_text); f.write('\n')
				finally: f.close()
				self.header.clear() # if the user touched the header in the build dir!
				self.cfg.impl.process_precompile_task(self, sched_ctx.lock)
				if False:
					# We create a file with a #error to ensure the pch is used.
					f = open(self.header.path, 'w')
					try: f.write('#error pre-compiled header missed\n');
					finally: f.close()
		finally: sched_ctx.lock.acquire()

	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			sig = Sig(self.source_text)
			sig.update(self.cfg.cxx_sig)
			sig = self._sig = sig.digest()
			return sig

class PreCompileTasks(ModDepPhases, ProjectTask):
	def __init__(self, name, base_cfg):
		ModDepPhases.__init__(self)
		ProjectTask.__init__(self, base_cfg.project)
		self.name = name
		self.base_cfg = base_cfg

	@property
	def cfg(self):
		try: return self._cfg
		except AttributeError:
			self._cfg = self.base_cfg.clone()
			return self._cfg

	def __str__(self): return 'pre-compile ' + self.name + ' (pic-or-not)'

	@property
	def source_text(self): return '#error ' + str(self.__class__) + ' did not redefine default source text.\n'

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
			pic_task = PreCompileTasks._PicOrNotTask(self, pic = True)
			self._lib_task = pic_task
		else:
			non_pic_task = PreCompileTasks._PicOrNotTask(self, pic = False)
			self._lib_task = non_pic_task
		if self.cfg.pic:
			if pic_task is None: pic_task = PreCompileTasks._PicOrNotTask(self, pic = True)
			self._prog_task = pic_task
		else:
			if non_pic_task is None: non_pic_task = PreCompileTasks._PicOrNotTask(self, pic = False)
			self._prog_task = non_pic_task

	class _PicOrNotTask(_PreCompileTask):
		def __init__(self, parent_task, pic):
			_PreCompileTask.__init__(self, parent_task.name + (not pic and '-non' or '') + '-pic', parent_task.cfg)
			self.parent_task = parent_task
			self.pic = pic

		@property
		def source_text(self): return self.parent_task.source_text

		def __call__(self, sched_ctx):
			for x in sched_ctx.parallel_wait(self.parent_task): yield x
			self.private_deps = self.parent_task.private_deps
			self.public_deps = self.parent_task.public_deps
			self.result = self.parent_task.result
			try: self.parent_task._cxx_phase_done
			except AttributeError:
				self.parent_task.do_cxx_phase()
				self.parent_task._cxx_phase_done = True
			self.cfg.pic = self.pic # this clones the parent cfg and changes the pic setting
			for x in _PreCompileTask.__call__(self, sched_ctx): yield x

		def apply_cxx_to(self, cfg):
			_PreCompileTask.apply_cxx_to(self, cfg)
			self.parent_task.apply_cxx_to(cfg)

	def do_cxx_phase(self): pass

class _BatchCompileTask(ProjectTask):
	def __init__(self, mod_task, sources):
		ProjectTask.__init__(self, mod_task.project)
		self.mod_task = mod_task
		self.sources = sources

	@property
	def cfg(self): return self.mod_task.cfg

	def __str__(self): return 'batch-compile ' + ' '.join([str(s) for s in self.sources])

	@property
	def uid(self): return self.mod_task.uid

	@property
	def target_dir(self): return self.mod_task.obj_dir
	
	@property
	def persistent_implicit_deps(self): return self.mod_task.persistent_implicit_deps

	def __call__(self, sched_ctx):
		if False: yield
		self.target_dir.make_dir()
		self.target_dir.actual_children # not needed, just an optimisation
		sched_ctx.lock.release()
		try:
			if not silent:
				color = color_bg_fg_rgb((0, 150, 180), (255, 255, 255))
				if self.cfg.pic: pic = 'pic'; color += ';1'
				else: pic = 'non-pic';
				s = [str(s) for s in self.sources]
				s.sort()
				self.print_desc_multi_column_format('batch-compiling ' + pic + ' objects from c++', s, color)
			self._actual_sources = []
			for s in self.sources:
				node = self.target_dir / self.mod_task._unique_base_name(s)
				if not node.exists:
					f = open(node.path, 'w')
					try: f.write('#include "%s"\n' % s.rel_path(self.target_dir))
					finally: f.close()
				self._actual_sources.append(node)
			self.cfg.impl.process_cxx_task(self, sched_ctx.lock)
		finally: sched_ctx.lock.acquire()

class ModTask(ModDepPhases, ProjectTask):
	class Kinds(object):
		HEADERS = 0
		PROG = 1
		LIB = 2 # TODO allow the developer to specify that a lib is not dll-aware
		LOADABLE = 3

	def __init__(self, name, kind, base_cfg, *aliases, **kw):
		if len(aliases) == 0: aliases = (name,)
		ModDepPhases.__init__(self)
		ProjectTask.__init__(self, base_cfg.project)
		self.name = name
		self.kind = kind
		self.base_cfg = base_cfg
		self.sources = []
		if kind == ModTask.Kinds.HEADERS:
			#self.cxx_phase = ModTask._CxxPhaseCallbackTask(self)
			self.cxx_phase = kw['cxx_phase']
			self.project.add_task_aliases(self.cxx_phase, *aliases)
		else:
			self.mod_phase = ModTask._ModPhaseCallbackTask(self)
			self.project.add_task_aliases(self.mod_phase, *aliases)

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

	@property
	def expose_private_deep_deps(self):
		try: return self._expose_private_deep_deps
		except AttributeError:
			self._expose_private_deep_deps = \
				(not self.ld or self.kind == ModTask.Kinds.PROG and self.cfg.static_prog) and \
				self.kind != ModTask.Kinds.HEADERS
			return self._expose_private_deep_deps

	def apply_mod_to(self, cfg):
		if not ModDepPhases.apply_mod_to(self, cfg): return
		if self.kind != ModTask.Kinds.HEADERS:
			if not self.target_dev_dir in cfg.lib_paths: cfg.lib_paths.append(self.target_dev_dir)
			cfg.libs.append(self.name)

	def __str__(self):
		if self.kind != ModTask.Kinds.HEADERS: return 'deps of module ' + str(self.target)
		else: return 'deps of headers ' + self.name

	@property
	def uid(self): return self.name

	@property
	def obj_dir(self):
		try: return self._obj_dir
		except AttributeError:
			self.project.bld_dir.lock.acquire()
			try: self._obj_dir = self.project.bld_dir / 'modules' / self.name
			finally: self.project.bld_dir.lock.release()
			return self._obj_dir

	@property
	def targets(self):
		try: return self._targets
		except AttributeError:
			self._targets = self.cfg.impl.mod_task_targets(self)
			return self._targets
	
	@property
	def target(self):
		try: return self._target
		except AttributeError:
			self._target = self.cfg.impl.mod_task_target_dir(self) / self.cfg.impl.mod_task_target_name(self)
			return self._target

	@property
	def target_dir(self): return self.target.parent
	
	@property
	def target_dev_dir(self):
		try: return self._target_dev_dir
		except AttributeError:
			self._target_dev_dir = self.cfg.impl.mod_task_target_dev_dir(self)
			return self._target_dev_dir

	@property
	def target_dev_name(self):
		try: return self._target_dev_name
		except AttributeError:
			self._target_dev_name = self.cfg.impl.mod_task_target_dev_name(self)
			return self._target_dev_name

	@property
	def ld(self):
		try: return self._ld
		except AttributeError:
			if self.kind == ModTask.Kinds.HEADERS: self._ld = False
			elif self.kind == ModTask.Kinds.PROG: self._ld = True
			else: self._ld = self.cfg.shared
			return self._ld

	@property
	def persistent_implicit_deps(self): return self.persistent[2]

	class _ModPhaseCallbackTask(Task):
		def __init__(self, mod_task):
			Task.__init__(self)
			self.mod_task = mod_task

		def __str__(self): return 'build module ' + str(self.mod_task.target)
		def __call__(self, sched_ctx):
			for x in self.mod_task._mod_phase_callback(sched_ctx): yield x

	def do_mod_phase(self): pass

	def _mod_phase_callback(self, sched_ctx):
		for x in sched_ctx.parallel_wait(self): yield x
		self.do_ensure_deps()
		if self.cxx_phase is not None: sched_ctx.parallel_no_wait(self.cxx_phase)
		if not self.ld:
			# For static archives, we don't need to wait for the deps,
			# but we want them to be done when the build finishes so that the resulting archive can be used.
			deps = (dep.mod_phase for dep in self.all_deps if dep.mod_phase is not None)
			sched_ctx.parallel_no_wait(*deps)
		else:
			# For shared libs and programs, we need all deps before linking.
			# We schedule them in advance, and don't wait for them right now, but just before linking.
			deps = self.topologically_sorted_unique_deep_deps(expose_private_deep_deps=True) # XXX or is expose_private_deep_deps=None enough?
			deps_mod_phases = [dep.mod_phase for dep in deps if dep.mod_phase is not None]
			sched_ctx.parallel_no_wait(*deps_mod_phases)
		for x in self.do_deps_cxx_phases(sched_ctx): yield x
		if len(self.cfg.pkg_config) != 0:
			self.cfg.cxx_sig # compute the signature before, because we don't need pkg-config cxx flags in the cfg sig
			pkg_config_cxx_flags_task = _PkgConfigCxxFlagsTask.shared(self.project, self.cfg.pkg_config)
			for x in sched_ctx.parallel_wait(pkg_config_cxx_flags_task): yield x
			pkg_config_cxx_flags_task.apply_to(self.cfg)
			if self.ld:
				pkg_config_ld_flags_task = _PkgConfigLdFlagsTask.shared(self.project, self.cfg.pkg_config,
				 	# XXX pkg-config and static/shared (alternative is self.cfg.static_prog or not self.cfg.shared)
					expose_private_deep_deps=self.cfg.static_prog)
				sched_ctx.parallel_no_wait(pkg_config_ld_flags_task)
		self.do_mod_phase()
		try: state = self.persistent
		except KeyError:
			if __debug__ and is_debug: debug('task: no state: ' + str(self))
			state = self.persistent = None, None, {}
			self._type_changed = False
			changed_sources = self.sources
		else:
			self._type_changed = state[1] != self.ld
			if __debug__ and is_debug and self._type_changed: debug('task: mod type changed: ' + str(self))
			changed_sources = deque()
			implicit_deps = state[2]
			for s in self.sources:
				try: had_failed, old_cxx_sig, deps, old_dep_sig = implicit_deps[s]
				except KeyError:
					# This is a new source.
					if __debug__ and is_debug: debug('task: no state: ' + str(s))
					changed_sources.append(s)
					continue
				if had_failed:
					# The compilation failed the last time.
					# We place this source first in the deque so that it is compiled first,
					# and hence we can give the fastest feedback in the usage cycle "fix some compilation errors then retry to build".
					if __debug__ and is_debug: debug('task: retry previously failed: ' + str(s))
					changed_sources.appendleft(s)
					continue
				try: dep_sigs = [dep.sig for dep in deps]
				except OSError:
					# A cached implicit dep does not exist anymore.
					if __debug__ and is_debug: debug('cpp: deps not found: ' + str(s))
					changed_sources.append(s)
					continue
				if old_dep_sig != Sig(''.join(dep_sigs)).digest():
					# The cached implicit deps changed.
					if __debug__ and is_debug: debug('cpp: deps changed: ' + str(s))
					changed_sources.append(s)
					continue
				if old_cxx_sig != self.cfg.cxx_sig:
					if __debug__ and is_debug: debug('task: cxx sig changed: ' + str(s))
					changed_sources.append(s)
					continue
				if self.cfg.check_missing:
					self.obj_dir.lock.acquire()
					try:
						try: self.obj_dir.actual_children # not needed, just an optimisation
						except OSError: pass
					finally: self.obj_dir.lock.release()
					o = self.obj_dir / self._obj_name(s)
					if not o.exists:
						if __debug__ and is_debug: debug('task: target missing: ' + str(o))
						changed_sources.append(s)
						continue
				if __debug__ and is_debug: debug('task: skip: no change: ' + str(s))
		need_process = False
		# For shared libs and programs, we need all deps before linking.
		# So these are parts of the tasks we need to process before linking.
		tasks = self.ld and deps_mod_phases or []
		if len(changed_sources) != 0:
			need_process = True
			batches = []
			for i in xrange(sched_ctx.thread_count): batches.append([])
			i = 0
			for s in changed_sources:
				batches[i].append(s)
				i = (i + 1) % sched_ctx.thread_count
			for b in batches:
				if len(b) == 0: break
				tasks.append(_BatchCompileTask(self, b))
		elif self.cfg.check_missing:
			for t in self.targets:
				if not t.exists:
					if __debug__ and is_debug: debug('task: target missing: ' + str(t))
					changed_sources = self.sources
					need_process = True
					break
		# Before linking, we wait for the compile tasks to complete.
		# For shared libs and programs, we also need all deps before linking.
		# We've scheduled them in advance, and now we wait for them too.
		# Note: When linking a shared lib on platforms that support -Wl,--undefined,
		#       which is the default on linux, we could go on even without all deps.
		#       Linking programs needs all deps, however.
		for x in sched_ctx.parallel_wait(*tasks): yield x
		if self.ld:
			for dep in self.topologically_sorted_unique_deep_deps(expose_private_deep_deps=None):
				dep.apply_mod_to(self.cfg) # ordering matters for sig
			if not need_process:
				for dep in self.all_deps:
					# When a dependant lib is a static archive, or changes its type from static to shared, we need to relink.
					# When the check-missing option is on, we also relink to check that external symbols still exist.
					try: need_process = dep._needed_process and (not dep.ld or dep._type_changed or self.cfg.check_missing)
					except AttributeError: continue # not a lib task
					if need_process:
						if __debug__ and is_debug: debug('task: dep lib task changed: ' + str(self) + ' ' + str(dep))
						break
			if len(self.cfg.pkg_config) != 0:
				self.cfg.ld_sig # compute the signature before, because we don't need pkg-config ld flags in the cfg sig
		if not need_process and state[0] != self._mod_sig:
				if __debug__ and is_debug: debug('task: mod sig changed: ' + str(self))
				changed_sources = self.sources
				need_process = True
		if not need_process:
			implicit_deps = state[2]
			if len(implicit_deps) > len(self.sources):
				# Some source has been removed from the list of sources to build.
				need_process = True
		if not need_process:
			if __debug__ and is_debug: debug('task: skip: no change: ' + str(self))
		else:
			if self.ld and len(self.cfg.pkg_config) != 0:
					for x in sched_ctx.parallel_wait(pkg_config_ld_flags_task): yield x
					pkg_config_ld_flags_task.apply_to(self.cfg)
			self.target_dir.make_dir()
			if self.kind != ModTask.Kinds.PROG and self.target_dir is not self.target_dev_dir: self.target_dev_dir.make_dir()
			sched_ctx.lock.release()
			try:
				implicit_deps = state[2]
				if len(implicit_deps) == len(self.sources):
					source_states = implicit_deps
					removed_obj_names = None
				else:
					# remove old sources from implicit deps dictionary
					source_states = {}
					for s in self.sources: source_states[s] = implicit_deps[s]
					if self.ld: removed_obj_names = None
					else:
						# remove old objects from static archive
						removed_obj_names = []
						for s in implicit_deps:
							if not s in self.sources: removed_obj_names.append(self._obj_name(s))
				if self.ld: sources = self.sources
				else: sources = changed_sources
				if not silent:
					if not self.ld: desc = 'archiving and indexing static lib'; color = color_bg_fg_rgb((120, 100, 120), (255, 255, 255))
					elif self.kind == ModTask.Kinds.PROG:
						if self.cfg.static_prog: shared = 'static'; color = color_bg_fg_rgb((0, 180, 0), (255, 255, 255))
						else: shared = 'dynamic'; color = color_bg_fg_rgb((130, 180, 0), (255, 255, 255))
						if self.cfg.pic: pic = 'pic'; color += ';1'
						else: pic = 'non-pic'
						desc = 'linking ' + shared + ' ' + pic + ' program'
					elif self.kind == ModTask.Kinds.LOADABLE: desc = 'linking loadable module'; color = color_bg_fg_rgb((180, 150, 80), (255, 255, 255))
					else: desc = 'linking shared lib'; color = color_bg_fg_rgb((150, 150, 0), (255, 255, 255))
					plus = not self.ld and '+' or ''
					if __debug__ and is_debug: s = [plus + self._obj_name(s) + '(' + str(s) + ')' for s in sources]
					else: s = [plus + self._obj_name(s) for s in sources]
					if removed_obj_names is not None: s += ['-' + o for o in removed_obj_names]
					s.sort()
					self.print_desc_multi_column_format(desc + ' ' + str(self.target) + ' from objects', s, color)
				self.cfg.impl.process_mod_task(self, [self._obj_name(s) for s in sources], removed_obj_names)
				self.persistent = self._mod_sig, self.ld, source_states
			finally: sched_ctx.lock.acquire()
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
			if self.kind not in (ModTask.Kinds.PROG, ModTask.Kinds.HEADERS) and \
				self.target_dir is not self.target_dev_dir: sig.update(self.target_dev_dir.abs_path)
			if self.ld: sig.update(self.cfg.ld_sig)
			else: sig.update(self.cfg.ar_ranlib_sig)
			self.__mod_sig = sig = sig.digest()
			return sig

class _PkgConfigTask(CheckTask):
	def __init__(self, project, pkgs):
		CheckTask.__init__(self, project)
		self.pkgs = pkgs

	@property
	def prog(self): return 'pkg-config'

	def __str__(self): return 'check pkg-config ' + ' '.join(self.what_args) + ' ' + ' '.join(self.pkgs)

	@property
	def desc(self):
		try: return self._desc
		except AttributeError:
			self._desc = self.prog + ' ' + self.what_desc + ' ' + ' '.join(self.pkgs)
			return self._desc

	@property
	def what_desc(self): raise Exception, str(self.__class__) + ' did not redefine the property.'
	
	@property
	def what_args(self): raise Exception, str(self.__class__) + ' did not redefine the property.'

	@property
	def args(self): return [self.prog] + self.pkgs + self.what_args

	@property
	def uid(self):
		try: return self._uid
		except AttributeError:
			pkgs = self.pkgs
			pkgs.sort()
			self._uid = ' '.join(pkgs) + ' ' + ' '.join(self.what_args)
			return self._uid

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

class _PkgConfigFlagsTask(_PkgConfigTask):
	def do_check_and_set_result(self, sched_ctx):
		if False: yield
		r, out, err = exec_subprocess_pipe(self.args, silent = True)
		if r != 0: raise Exception, r
		self.results = out.split()

	if __debug__ and is_debug:
		@property
		def result_display(self): return ' '.join(self.result), '32'
	else:
		@property
		def result_display(self): return 'ok', '32'

	def apply_to(self): raise Exception, str(self.__class__) + ' did not redefine the method.'

class _PkgConfigCxxFlagsTask(_PkgConfigFlagsTask):
	@classmethod
	def shared(class_, project, pkgs):
		try: pkg_configs = project.cxx_pkg_configs
		except AttributeError: pkg_configs = project.cxx_pkg_configs = {}
		key = '--cflags ' + ' '.join(pkgs)
		try: return pkg_configs[key]
		except KeyError:
			task = pkg_configs[key] = class_(project, pkgs)
			return task

	@property
	def what_desc(self): return 'cxx flags'
	
	@property
	def what_args(self): return ['--cflags']

	def apply_to(self, cfg): cfg.cxx_flags += self.result

class _PkgConfigLdFlagsTask(_PkgConfigFlagsTask):
	@classmethod
	def shared(class_, project, pkgs, expose_private_deep_deps):
		try: pkg_configs = project.cxx_pkg_configs
		except AttributeError: pkg_configs = project.cxx_pkg_configs = {}
		key = '--libs' + (expose_private_deep_deps and ' --static ' or ' ') + ' '.join(pkgs)
		try: return pkg_configs[key]
		except KeyError:
			task = pkg_configs[key] = class_(project, pkgs, expose_private_deep_deps)
			return task

	def __init__(self, project, pkgs, expose_private_deep_deps):
		_PkgConfigFlagsTask.__init__(self, project, pkgs)
		self.expose_private_deep_deps = expose_private_deep_deps

	@property
	def what_desc(self):
		if self.expose_private_deep_deps: return 'static ld flags'
		else: return 'shared ld flags'
	
	@property
	def what_args(self):
		if self.expose_private_deep_deps: return ['--libs', '--static']
		else: return ['--libs']

	def apply_to(self, cfg): cfg.ld_flags += self.result

class PkgConfigCheckTask(_PkgConfigTask, ModDepPhases):
	@classmethod
	def shared(class_, project, pkgs):
		try: pkg_configs = project.cxx_pkg_configs
		except AttributeError: pkg_configs = project.cxx_pkg_configs = {}
		key = ' '.join(pkgs)
		try: return pkg_configs[key]
		except KeyError:
			task = pkg_configs[key] = class_(project, pkgs)
			return task

	def __init__(self, *args, **kw):
		ModDepPhases.__init__(self)
		_PkgConfigTask.__init__(self, *args, **kw)

	def __call__(self, sched_ctx):
		for x in ModDepPhases.__call__(self, sched_ctx): yield x
		for x in _PkgConfigTask.__call__(self, sched_ctx): yield x

	def apply_cxx_to(self, cfg):
		if not ModDepPhases.apply_cxx_to(self, cfg): return
		cfg.pkg_config += self.pkgs
		
	@property
	def what_desc(self): return 'existence'
	
	@property
	def what_args(self): return ['--exists']

	def do_check_and_set_result(self, sched_ctx):
		if False: yield
		try: r = exec_subprocess(self.args)
		except Exception, e:
			if __debug__ and is_debug: debug('cfg: ' + self.desc + ': exception: ' + str(e))
			r = 1
		# note: in case of a positive result, we could as well store a positive result for each individual packages
		self.results = r == 0

class MultiBuildCheckTask(CheckTask, ModDepPhases):
	def __init__(self, name, base_cfg, pipe_preproc=False, compile=True, link=True):
		CheckTask.__init__(self, base_cfg.project)
		ModDepPhases.__init__(self)
		self.name = name
		self.base_cfg = base_cfg
		self.pipe_preproc = pipe_preproc
		self.compile = compile
		self.link = link

	def __call__(self, sched_ctx):
		for x in ModDepPhases.__call__(self, sched_ctx): yield x
		for x in CheckTask.__call__(self, sched_ctx): yield x

	@property
	def cfg(self):
		try: return self._cfg
		except AttributeError:
			self._cfg = self.base_cfg.clone()
			if self.link: self.cfg.shared = False # build a program
			self.apply_to(self._cfg)
			return self._cfg

	def apply_cxx_to(self, cfg):
		if not ModDepPhases.apply_cxx_to(self, cfg): return
		self.apply_to(cfg)

	def apply_to(self, cfg): pass
		
	@property
	def source_text(self): return '#error ' + str(self.__class__) + ' did not redefine default source text.\n'

	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			sig = Sig(self.source_text)
			sig.update(self.base_cfg.cxx_sig)
			if self.link: sig.update(self.base_cfg.ld_sig)
			sig = self._sig = sig.digest()
			return sig

	@property
	def uid(self): return self.name

	@property
	def desc(self): return self.name

class BuildCheckTask(MultiBuildCheckTask):
	@property
	def _prog_source_text(self):
		if self.pipe_preproc or not self.link: return self.source_text
		else: return self.source_text + '\nint main() { return 0; }\n'

	@property
	def bld_dir(self):
		try: return self._bld_dir
		except AttributeError:
			self.project.bld_dir.lock.acquire()
			try: self._bld_dir = self.project.bld_dir / 'checks' / self.name
			finally: self.project.bld_dir.lock.release()
			return self._bld_dir

	def do_check_and_set_result(self, sched_ctx):
		if False: yield
		sched_ctx.lock.release()
		try:
			dir = self.bld_dir
			dir.make_dir(dir.parent)
			r, out, err = self.cfg.impl.process_build_check_task(self)
			if False: # no real need for a log file, the --verbose=exec option gives the same details
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
			if self.pipe_preproc: self.results = r == 0, out
			else: self.results = r == 0
		finally: sched_ctx.lock.acquire()
