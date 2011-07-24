#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2007-2011 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os, threading
from collections import deque

from wonderbuild import UserReadableException
from wonderbuild.logger import out, is_debug, debug, colored, color_bg_fg_rgb, silent
from wonderbuild.signature import Sig
from wonderbuild.option_cfg import OptionCfg
from wonderbuild.fhs import FHS
from wonderbuild.task import Persistent, Task
from wonderbuild.check_task import CheckTask, ok_color, failed_color
from wonderbuild.subprocess_wrapper import exec_subprocess, exec_subprocess_pipe

class DestPlatform(object):
	def __init__(self):
		self.bin_fmt = None
		self.os = None
		self.arch = None
		self.pic_flag_defines_pic = None

	def clone(self, class_ = None):
		if class_ is None: class_ = self.__class__
		if __debug__ and is_debug: debug('cfg: dest platform: clone: ' + str(class_))
		c = class_()
		c.bin_fmt = self.bin_fmt
		c.os = self.os
		c.arch = self.arch
		c.pic_flag_defines_pic = self.pic_flag_defines_pic
		return c

	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			sig = Sig(self.bin_fmt, self.os, self.arch)
			if self.pic_flag_defines_pic is not None: sig.update(str(self.pic_flag_defines_pic))
			sig = self._sig = sig.digest()
			return sig
			
class BuildCfg(object):
	def __init__(self, project):
		self.project = project
		# client cfg
		self.defines = {}
		self.include_paths = deque()
		self.cxx_flags = []
		self.lib_paths = deque()
		self.libs = []
		self.static_libs = []
		self.shared_libs = []
		self.ld_flags = []
		self.pkg_config = []
		self.frameworks = set() # for darwin
		# build cfg
		self.lang = 'c++'
		self.cxx_prog = self.ld_prog = self.ar_prog = self.ranlib_prog = None
		self.pic = self.shared = self.static_prog = None
		self.includes = deque()
		self.pch = None
		self.check_missing = False
		self.ld_on_shared_dep_impl_change = False
		self.fhs = FHS.shared(project)
		self.impl = self.kind = self.version = None
		self.dest_platform = DestPlatform()
		self.use_input_abs_paths = False
		self.shared_checks = project

	def clone(self, class_ = None):
		if class_ is None: class_ = self.__class__
		if __debug__ and is_debug: debug('cfg: clone: ' + str(class_))
		c = class_(self.project)
		# client cfg
		c.defines.update(self.defines)
		c.include_paths.extend(self.include_paths)
		c.cxx_flags += self.cxx_flags
		c.lib_paths.extend(self.lib_paths)
		c.libs += self.libs
		c.static_libs += self.static_libs
		c.shared_libs += self.shared_libs
		c.ld_flags += self.ld_flags
		c.pkg_config += self.pkg_config
		c.frameworks |= self.frameworks
		# build cfg
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
		c.ld_on_shared_dep_impl_change = self.ld_on_shared_dep_impl_change
		c.fhs = self.fhs
		c.impl = self.impl
		c.kind = self.kind
		c.version = self.version
		c.dest_platform = self.dest_platform.clone() # not sure it's useful to clone
		c.shared_checks = self.shared_checks
		c.use_input_abs_paths = self.use_input_abs_paths
		return c

	@property
	def _common_sig(self):
		try: return self.__common_sig
		except AttributeError:
			sig = Sig(self.impl.common_env_sig)
			e = os.environ.get('PATH', None)
			if e is not None: sig.update(e)
			sig.update(self.lang, self.kind, str(self.version), self.dest_platform.sig)
			if len(self.pkg_config) != 0:
				sig.update(_PkgConfigTask.env_sig())
				# Note: there is no need to sign self.pkg_config itself since this ends up as cxx_flags and ld_flags
			sig.update(*sorted(self.frameworks))
			sig = self.__common_sig = sig.digest()
			return sig
		
	@property
	def cxx_sig(self):
		try: return self._cxx_sig
		except AttributeError:
			sig = Sig(self._common_sig, self.cxx_prog, str(self.pic))
			for k in sorted(self.defines.iterkeys()):
				sig.update(k)
				v = self.defines[k]
				if v is not None: sig.update(str(v))
			sig.update(*(p.abs_path for p in self.include_paths))
			if self.pch is not None: sig.update(self.pch.sig)
			sig.update(*(i.sig for i in self.includes))
			sig.update(*self.cxx_flags)
			sig.update(self.impl.cxx_env_sig)
			sig = self._cxx_sig = sig.digest()
			return sig

	@property
	def _common_mod_sig(self):
		try: return self.__common_mod_sig
		except AttributeError:
			sig = Sig(self._common_sig, str(self.shared), str(self.static_prog))
			sig.update(*(p.abs_path for p in self.lib_paths))
			sig.update(*self.libs)
			sig.update(*self.static_libs)
			sig.update(*self.shared_libs)
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

	# used in cfg.impl for PreCompileTask, BatchCompileTask and ModTask
	def bld_rel_path(self, node):
		path = node.rel_path(self.project.bld_dir)
		if not os.path.isabs(path): path = os.path.join(os.pardir, os.pardir, path)
		return path
	# used in cfg.impl for PreCompileTask, BatchCompileTask and ModTask
	def bld_rel_path_or_abs_path(self, node): return self.use_input_abs_paths and node.abs_path or self.bld_rel_path(node)
	# used in cfg.impl for PreCompileTask, BatchCompileTask and ModTask
	def bld_rel_name_or_abs_path(self, node): return self.use_input_abs_paths and node.abs_path or node.name

	# generic cxx args not tied to a particular PreCompileTask or BatchCompileTask
	@property
	def cxx_args(self):
		try: return self._cxx_args
		except AttributeError:
			args = self._cxx_args = self.impl.cfg_cxx_args(self)
			if __debug__ and is_debug: debug('cfg: cxx: build: cxx: ' + str(args))
			return args

	# generic ld args not tied to a particular ModTask
	@property
	def ld_args(self):
		try: return self._ld_args
		except AttributeError:
			args = self._ld_args = self.impl.cfg_ld_args(self)
			if __debug__ and is_debug: debug('cfg: cxx: build: ld: ' + str(args))
			return args

	# generic ar and ranlib args not tied to a particular ModTask
	@property
	def ar_ranlib_args(self):
		try: return self._ar_ranlib_args
		except AttributeError:
			args = self._ar_ranlib_args = self.impl.cfg_ar_ranlib_args(self)
			if __debug__ and is_debug: debug('cfg: cxx: build: ar ranlib: ' + str(args))
			return args

class UserBuildCfgTask(BuildCfg, OptionCfg, Persistent, Task):
	def clone(self, class_ = None):
		if class_ is None: class_ = BuildCfg
		return class_.clone(self, class_)

	# OptionCfg
	signed_os_environ = set(['PATH', 'CXX', 'CXXFLAGS', 'LD', 'LDFLAGS', 'AR', 'RANLIB'])

	# OptionCfg
	signed_options = set([
		'cxx',
		'cxx-flags',
		'ld',
		'ld-flags',
		'ar',
		'ranlib',
		'static',
		'pic-static'
	])

	# OptionCfg(OptionDecl)
	known_options = signed_options | set(['check-missing', 'relink-on-shared-dep-impl-change', 'input-abs-paths'])

	# OptionCfg(OptionDecl)
	@staticmethod
	def generate_option_help(help):
		help['check-missing'] = ('[yes|no]', 'check for missing built files; rebuild files you manually deleted in the build dir', 'yes')

		help['relink-on-shared-dep-impl-change'] = ('[yes|no]',
			'relink clients of a shared lib if its implementation changed; '
			'Normaly when only the implementation changed, and not the interface, clients are not impacted',
			'no')

		help['input-abs-paths'] = ('[yes|no]',
			'use absolute paths for source input files to the compiler. '
			'Using absolute paths may let you click on error lines to open the files.',
			'no => use paths relative to the build dir')

		help['cxx']           = ('<prog>', 'use <prog> as c++ compiler', 'CXX env var: ' + os.environ.get('CXX', '(not set)'))
		help['cxx-flags']     = ('[flags]', 'use specific c++ compiler flags', 'CXXFLAGS env var: ' + os.environ.get('CXXFLAGS', '(not set)'))
		help['ld']            = ('<prog>', 'use <prog> as shared lib and program linker', 'LD env var: ' + os.environ.get('LD', '(not set)'))
		help['ld-flags']      = ('[flags]', 'use specific linker flags', 'LDFLAGS env var: ' + os.environ.get('LDFLAGS', '(not set)'))
		help['ar']            = ('<prog>', 'use <prog> as static lib archiver', 'AR env var: ' + os.environ.get('AR', '(not set, defaults to ar on posix)'))
		help['ranlib']        = ('<prog>', 'use <prog> as static lib archive indexer', 'RANLIB env var: ' + os.environ.get('RANLIB', '(not set, defaults to using the ar s flag on posix)'))
		
		help['static'] = ('<no|libs|full>',
			'no: build dynamic, shared libs and programs\n'
			'libs: build libs as static archives (rather than dynamic, shared libs),\n'
			'full: like libs but also statically link programs (rather than dynamically using shared libs)',
			'no')
		help['pic-static'] = ('[yes|no]',
			'instruct the compiler to emit pic code even for static libs and programs; '
			'shared libs are of course always pic regardless of this option.',
			'no => non-pic for static libs and programs')

		# posix compiler options -O -g -s
		#help['optim']        = ('<0|1|n>', '...', '0')
		#help['debug']        = ('<yes|no>', '...', 'no')
		#help['strip']        = ('<yes|no>', '...', 'no')

	@staticmethod
	def shared(project):
		try: build_cfg_task = project.__cxx_user_build_cfg_task
		except AttributeError: build_cfg_task = project.__cxx_user_build_cfg_task = UserBuildCfgTask(project)
		return build_cfg_task
	
	def __init__(self, project):
		BuildCfg.__init__(self, project)
		OptionCfg.__init__(self, project)
		Persistent.__init__(self, project.persistent, str(self.__class__))
		Task.__init__(self)
	
	# Task
	def __call__(self, sched_ctx):
		o = self.options

		self.check_missing = o.get('check-missing', 'yes') != 'no'
		self.ld_on_shared_dep_impl_change = o.get('relink-on-shared-dep-impl-change', 'no') != 'no'
		self.use_input_abs_paths = o.get('input-abs-paths', 'no') != 'no'
		
		try:
			old_sig, \
			self.cxx_prog, self.cxx_flags, self.pic, \
			self.shared, self.static_prog, self.ld_prog, self.ld_flags, \
			self.ar_prog, self.ranlib_prog = \
				self.persistent
		except KeyError: old_sig = None
		if old_sig != self.options_sig:
			if __debug__ and is_debug: debug('cfg: cxx: user: parsing options')

			self.cxx_prog = o.get('cxx', None) or os.environ.get('CXX', None)
			if 'cxx-flags' in o: self.cxx_flags = o['cxx-flags'].split()
			else:
				e = os.environ.get('CXXFLAGS', None)
				if e is not None: self.cxx_flags = e.split()
				else: self.cxx_flags = []

			static = o.get('static', 'no')
			self.shared = static == 'no'
			self.static_prog = static == 'full'
			
			self.pic = o.get('pic-static', 'no') != 'no' # this is for programs and static libs only
			
			self.ld_prog = o.get('ld', None) or os.environ.get('LD', None)
			if 'ld-flags' in o: self.ld_flags = o['ld-flags'].split()
			else:
				e = os.environ.get('LDFLAGS', None)
				if e is not None: self.ld_flags = e.split()
				else: self.ld_flags = []
			self.ar_prog = o.get('ar', None) or os.environ.get('AR', None)
			self.ranlib_prog = o.get('ranlib', None) or os.environ.get('RANLIB', None)
			
			if self.cxx_prog    is not None: self.print_desc('user-provided-build-cfg-flags: cxx: ' + self.cxx_prog)
			if len(self.cxx_flags) != 0    : self.print_desc('user-provided-build-cfg-flags: cxx flags: ' + str(self.cxx_flags))
			if self.ld_prog     is not None: self.print_desc('user-provided-build-cfg-flags: ld: ' + self.ld_prog)
			if len(self.ld_flags) != 0     : self.print_desc('user-provided-build-cfg-flags: ld flags: ' + str(self.ld_flags))
			if self.ar_prog     is not None: self.print_desc('user-provided-build-cfg-flags: ar: ' + self.ar_prog)
			if self.ranlib_prog is not None: self.print_desc('user-provided-build-cfg-flags: ranlib: ' + self.ranlib_prog)

			self.persistent = \
				self.options_sig, \
				self.cxx_prog, self.cxx_flags, self.pic, \
				self.shared, self.static_prog, self.ld_prog, self.ld_flags, \
				self.ar_prog, self.ranlib_prog

		if True or 'help' not in o: # XXX needs to be done because check tasks need the cfg impl sig
			from detect_impl import DetectImplCheckTask
			detect_impl = DetectImplCheckTask.shared(self)
			for x in sched_ctx.parallel_wait(detect_impl): yield x

class ModDepPhases(object): # note: doesn't derive form Task, but derived classes must also derive from Task
	def __init__(self):
		if __debug__ and is_debug: assert isinstance(self, Task) # note: doesn't derive form Task, but derived classes must also derive from Task
		self.private_deps = [] # of ModDepPhases
		self.public_deps = [] # of ModDepPhases
		self.cxx_phase = self.mod_phase = None

	@property
	def all_deps(self): return self.public_deps + self.private_deps

	if False:
		# Currently, it's the responsibility of derived classes to actually call the dep tasks, which they need to do since they want to check their results.
		# If we want to change this. We need changes in CheckTask. See code below.
		# called by derived classes that also derive from Task
		def __call__(self, sched_ctx):
			self.result = True
			for x in self.do_check_phase(sched_ctx): yield x
			if self.result and len(self.all_deps) != 0:
				for x in sched_ctx.parallel_wait(*self.all_deps): yield x
				self.result = min(bool(dep) for dep in self.all_deps)

	# can be overriden in derived classes to generate friendlier message when deps are unavailable
	def do_ensure_deps(self): 
		all_deps = self.all_deps
		if False:
			# Currently, it's the responsibility of derived classes to actually call the dep tasks, which they need to do since they want to check their results.
			if len(all_deps) != 0:
				for x in sched_ctx.parallel_wait(*all_deps): yield x
		for dep in all_deps:
			if not dep:
				desc = str(self.mod_phase or self.cxx_phase or self) + ' requires the following dep: '
				try: dep.do_ensure_deps()
				except UserReadableException, e: desc += str(dep.mod_phase or dep.cxx_phase or dep) + ',\nand ' + str(e)
				else: desc += str(dep)
				raise UserReadableException, desc
		if __debug__ and is_debug: assert self.result

	# bool result is compatible with CheckTask.result
	# This is merged in MultiBuildCheckTask which derives both from CheckTask and ModDepPhases.
	def _get_result(self):
		try: return self._result
		except AttributeError: raise Exception, 'did you forget to process the ' + str(self) + ' task?'
	def _set_result(self, value): self._result = value
	result = property(_get_result, _set_result)
	def __bool__(self): return self.result
	def __nonzero__(self): return self.__bool__() # __bool__ has become the default in python 3

	
	def apply_cxx_to(self, cfg): pass
	def apply_mod_to(self, cfg): pass
	
	def _do_deps_cxx_phases_and_apply_cxx_deep(self, sched_ctx):
		deep_deps = self._topologically_sorted_unique_deep_deps(expose_private_deep_deps=False)
		cxx_phases = (dep.cxx_phase for dep in deep_deps if dep.cxx_phase is not None)
		for x in sched_ctx.parallel_wait(*cxx_phases): yield x
		for dep in deep_deps: dep.apply_cxx_to(self.cfg) # ordering matters for sig

 	@property
	def _expose_private_deep_deps(self): return False

	def _topologically_sorted_unique_deep_deps(self, expose_private_deep_deps, expose_deep_mod_tasks=True):
		if expose_private_deep_deps: expose_private_deep_deps = None # called with True or False, but we use a tribool in the recursion
		result = deque(); seen = set() # ordering matters for sig, and static libs must appear after their clients
		def recurse(instance, root, expose_private_deps, expose_private_deep_deps, expose_deep_mod_tasks):
			if not root:
				if instance in seen: return
				seen.add(instance)
			for dep in expose_private_deps and instance.all_deps or instance.public_deps:
				if expose_deep_mod_tasks or not isinstance(dep, ModTask):
					if expose_private_deep_deps is None:
						recurse(dep, False,
							dep._expose_private_deep_deps, dep._expose_private_deep_deps and None,
							expose_deep_mod_tasks is not None and (expose_deep_mod_tasks or not isinstance(dep, ModTask) or None))
					else:
						recurse(dep, False,
							expose_private_deep_deps, expose_private_deep_deps,
							expose_deep_mod_tasks is not None and (expose_deep_mod_tasks or not isinstance(dep, ModTask) or None))
				else:
					if not dep in seen:
						result.appendleft(dep)
						seen.add(dep)
			if not root: result.appendleft(instance)
		recurse(self, True, True, expose_private_deep_deps, expose_deep_mod_tasks)
		return result

class _PreCompileTask(ModDepPhases, Task, Persistent):
	def __init__(self, name, base_cfg):
		ModDepPhases.__init__(self)
		Task.__init__(self)
		Persistent.__init__(self, base_cfg.project.persistent, name)
		self.name = name
		self.base_cfg = base_cfg

	@property
	def cfg(self):
		try: return self._cfg
		except AttributeError:
			self._cfg = self.base_cfg.clone()
			return self._cfg
	
	# Task
	def __call__(self, sched_ctx):
		if False: yield
		self.cxx_phase = _PreCompileTask._CxxPhaseCallbackTask(self)
	
	# ModDepPhases
	def apply_cxx_to(self, cfg): cfg.pch = self.header

	@property
	def source_text(self): return '#error ' + str(self.__class__) + ' did not redefine default source text.\n'

	def __str__(self): return 'deps of pre-compilation of ' + str(self.header)

	@property
	def header(self):
		try: return self._header
		except AttributeError:
			bld_dir = self.base_cfg.project.bld_dir
			bld_dir.lock.acquire()
			try: self._header = bld_dir / 'pre-compiled' / self.name / (self.name + '.private.' + {'c++': 'hpp', 'c': 'h', 'objective-c++': 'hpp', 'objective-c': 'h'}[self.base_cfg.lang])
			finally: bld_dir.lock.release()
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

		# Task		
		def __call__(self, sched_ctx):
			for x in self.pre_compile_task._cxx_phase_callback(sched_ctx): yield x

	def _cxx_phase_callback(self, sched_ctx):
		for x in sched_ctx.parallel_wait(self): yield x
		self.do_ensure_deps()
		
		# We need the headers of our deps.
		for x in self._do_deps_cxx_phases_and_apply_cxx_deep(sched_ctx): yield x
		
		if len(self.cfg.pkg_config) != 0:
			self.cfg.cxx_sig # compute the signature before, because we don't need pkg-config cxx flags in the cfg sig
			pkg_config_cxx_flags_task = _PkgConfigCxxFlagsTask.shared(self.cfg)
			for x in sched_ctx.parallel_wait(pkg_config_cxx_flags_task): yield x
			pkg_config_cxx_flags_task.apply_to(self.cfg)
		
		sched_ctx.lock.release()
		try:
			need_process = False

			cxx_sig = Sig(self.source_text)
			cxx_sig.update(self.cfg.cxx_sig)
			cxx_sig = cxx_sig.digest()

			try: old_cxx_sig, deps, old_dep_sig = self.persistent
			except KeyError:
				if __debug__ and is_debug: debug('task: no state: ' + str(self))
				need_process = True
			else:
				if old_cxx_sig != cxx_sig:
					if __debug__ and is_debug: debug('task: sig changed: ' + str(self))
					need_process = True
				else:
					try: dep_sigs = [dep.sig for dep in deps]
					except OSError:
						# A cached implicit dep does not exist anymore.
						if __debug__ and is_debug: debug('cpp: deps not found: ' + str(self.header))
						need_process = True
					else:
						if old_dep_sig != Sig(''.join(dep_sigs)).digest():
							# The cached implicit deps changed.
							if __debug__ and is_debug: debug('cpp: deps changed: ' + str(self.header))
							need_process = True
						elif self.cfg.check_missing:
							self.target_dir.lock.acquire()
							try:
								try: self.target_dir.actual_children # not needed, just an optimisation
								except OSError: pass
							finally: self.target_dir.lock.release()
							if not self.target.exists:
								if __debug__ and is_debug: debug('task: target missing: ' + str(self.target))
								need_process = True
			if not need_process:
				if __debug__ and is_debug: debug('task: skip: no change: ' + str(self.header))
			else:
				if not silent: 
					color = color_bg_fg_rgb((130, 50, 130), (255, 255, 255))
					if self.cfg.pic: pic = 'pic'; color += ';1'
					else: pic = 'non-pic'
					self.print_desc(str(self.header) + ': pre-compiling ' + pic + ' c++', color)
				self.header.parent.make_dir(self.header.parent)
				f = open(self.header.path, 'w')
				try: f.write(self.source_text); f.write('\n')
				finally: f.close()
				deps = self.cfg.impl.process_precompile_task(self, sched_ctx.lock)
				# We create a file with a #error to ensure the pch is used.
				f = open(self.header.path, 'w')
				try:
					f.write(
						'#error This is an intentional error to ensure the pre-compiled header is really used.\n'
						'// Below is the original file content that was pre-compiled to ' + self.target.rel_path(self.header.parent) + '\n'
					)
					f.write(self.source_text); f.write('\n')					
				finally: f.close()
				self.header.clear()
				dep_sigs = [d.sig for d in deps]
				self.persistent = cxx_sig, deps, Sig(''.join(dep_sigs)).digest()
		finally: sched_ctx.lock.acquire()

class PreCompileTasks(ModDepPhases, Task):
	def __init__(self, name, base_cfg):
		ModDepPhases.__init__(self)
		Task.__init__(self)
		self.name = name
		self.base_cfg = base_cfg

	@property
	def cfg(self):
		try: return self._cfg
		except AttributeError:
			self._cfg = self.base_cfg.clone()
			return self._cfg

	def __str__(self): return 'pre-compile ' + self.name + ' (pic-or-not)'

	source_text = '#error no source text defined.\n'

	@property
	def pic_task(self):
		try: return self._pic_task
		except AttributeError:
			self._pic_task = PreCompileTasks._PicOrNotTask(self, pic=True)
			return self._pic_task

	@property
	def non_pic_task(self):
		try: return self._non_pic_task
		except AttributeError:
			self._non_pic_task = PreCompileTasks._PicOrNotTask(self, pic=False)
			return self._non_pic_task

	def pic_or_not(self, cfg):
		if cfg.shared or cfg.pic: return self.pic_task
		else: return self.non_pic_task

	@property
	def lib_task(self):
		try: return self._lib_task
		except AttributeError:
			if self.cfg.shared or self.cfg.pic: self._lib_task = self.pic_task
			else: self._lib_task = self.non_pic_task
			return self._lib_task

	@property
	def prog_task(self):
		try: return self._prog_task
		except AttributeError:
			if self.cfg.pic: self._prog_task = self.pic_task
			else: self._prog_task = self.non_pic_task
			return self._prog_task

	class _PicOrNotTask(_PreCompileTask):
		def __init__(self, parent_task, pic):
			_PreCompileTask.__init__(self, parent_task.name + (not pic and '-non' or '') + '-pic', parent_task.cfg)
			self.parent_task = parent_task
			self.pic = pic

		@property
		def source_text(self): return self.parent_task.source_text

		# _PreCompileTask(Task)
		def __call__(self, sched_ctx):
			for x in sched_ctx.parallel_wait(self.parent_task): yield x
			self.private_deps = self.parent_task.private_deps
			self.public_deps = self.parent_task.public_deps
			self.result = self.parent_task.result
			try: self.parent_task.__cxx_phase_done
			except AttributeError:
				self.parent_task.do_cxx_phase()
				self.parent_task.__cxx_phase_done = True
			self.cfg.pic = self.pic # this clones the parent cfg and changes the pic setting
			for x in _PreCompileTask.__call__(self, sched_ctx): yield x

	def do_cxx_phase(self): pass

class _BatchCompileTask(Task):
	def __init__(self, mod_task, sources):
		Task.__init__(self)
		self.mod_task = mod_task
		self.sources = sources

	@property
	def cfg(self): return self.mod_task.cfg

	def __str__(self): return 'compile ' + self.mod_task.name + ': ' + ' '.join([str(s) for s in self.sources])

	@property
	def target_dir(self): return self.mod_task.obj_dir
	
	@property
	def persistent_implicit_deps(self): return self.mod_task.persistent[-1]

	# Task
	def __call__(self, sched_ctx):
		if False: yield
		self.target_dir.make_dir()
		self.target_dir.actual_children # not needed, just an optimisation
		sched_ctx.lock.release()
		try:
			if __debug__ and is_debug and not silent:
				color = color_bg_fg_rgb((0, 150, 180), (255, 255, 255))
				if self.cfg.pic: pic = 'pic'; color += ';1'
				else: pic = 'non-pic';
				s = [str(s) for s in self.sources]
				s.sort()
				self.print_desc_multicolumn_format(str(self.mod_task.target) + ': compiling ' + pic + ' objects from ' + self.cfg.lang, s, color)
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

class ModTask(ModDepPhases, Task, Persistent):
	class Kinds(object):
		HEADERS = 0
		PROG = 1
		LIB = 2 # TODO allow the developer to specify that a lib is not dll-aware
		LOADABLE = 3

	def __init__(self, name, kind, base_cfg, **kw):
		ModDepPhases.__init__(self)
		Task.__init__(self)
		Persistent.__init__(self, base_cfg.project.persistent, name)
		self.base_cfg = base_cfg
		self.name = name
		self.title = kw.get('title', name)
		self.description = kw.get('description', self.title)
		self.version_interface = kw.get('version_interface', 0)
		self.version_interface_min = kw.get('version_interface_min', 0)
		self.version_impl = kw.get('version_impl', 0)
		self.version_string = kw.get('version_string', '0')
		self.url = kw.get('url', None)
		self.kind = kind
		self.sources = []
		self.cxx_phase = kw.get('cxx_phase', None)
		self.mod_phase = ModTask._ModPhaseCallbackTask(self)
		base_cfg.project.add_task_aliases(self.mod_phase, name)
	
	@property
	def cfg(self):
		try: return self._cfg
		except AttributeError:
			cfg = self._cfg = self.base_cfg.clone()
			if self.kind in (ModTask.Kinds.HEADERS, ModTask.Kinds.PROG): cfg.shared = False
			else:
				if self.kind == ModTask.Kinds.LOADABLE: cfg.shared = True
				if cfg.shared and not cfg.pic:
					debug('cfg: cxx: mod: shared lib => overriding cfg to pic')
					cfg.pic = True
			return cfg

	# ModDepPhases
	@property
	def _expose_private_deep_deps(self):
		try: return self.__expose_private_deep_deps
		except AttributeError:
			self.__expose_private_deep_deps = \
				(not self.ld or self.kind == ModTask.Kinds.PROG and self.cfg.static_prog) and \
				self.kind != ModTask.Kinds.HEADERS
			return self.__expose_private_deep_deps

	# ModDepPhases
	def apply_mod_to(self, cfg):
		if self.kind != ModTask.Kinds.HEADERS:
			if not self.target_dev_dir in cfg.lib_paths: cfg.lib_paths.append(self.target_dev_dir)
			cfg.libs.append(self.name)

	def _unique_base_name(self, source):
		return source.rel_path(self.base_cfg.project.top_src_dir).replace(os.pardir, '_').replace(os.sep, ',')

	def _obj_name(self, source):
		name = self._unique_base_name(source)
		return name[:name.rfind('.')] + self.cfg.impl.cxx_task_target_ext

	@property
	def obj_dir(self):
		''' the dir node where intermediate object files are placed'''
		try: return self._obj_dir
		except AttributeError:
			self.base_cfg.project.bld_dir.lock.acquire()
			try: self._obj_dir = self.base_cfg.project.bld_dir / 'modules' / self.name
			finally: self.base_cfg.project.bld_dir.lock.release()
			return self._obj_dir

	@property
	def targets(self):
		''' the file nodes of all outputs: program, shared lib and its import lib, static archive. '''
		try: return self._targets
		except AttributeError:
			self._targets = self.cfg.impl.mod_task_targets(self)
			return self._targets
	
	@property
	def target(self):
		''' the file node of the runtime output: program, shared lib, or static archive.'''
		try: return self._target
		except AttributeError:
			self._target = self.target_dir / self.cfg.impl.mod_task_target_name(self)
			return self._target

	@property
	def target_dir(self):
		''' the dir node where the runtime output is placed, or where the static archive is placed. '''
		try: return self._target_dir
		except AttributeError:
			self._target_dir = self.cfg.impl.mod_task_target_dir(self)
			return self._target_dir
	
	@property
	def target_dev_dir(self):
		''' the dir node added to the library search path passed to clients in their linker command. '''
		try: return self._target_dev_dir
		except AttributeError:
			self._target_dev_dir = self.cfg.impl.mod_task_target_dev_dir(self)
			return self._target_dev_dir

	@property
	def target_dev_name(self):
		''' the library name passed to clients in their linker command. '''
		try: return self._target_dev_name
		except AttributeError:
			self._target_dev_name = self.cfg.impl.mod_task_target_dev_name(self)
			return self._target_dev_name

	@property
	def ld(self):
		''' a boolean that indicates whether the module is created by a linker.
			This is true for shared libs and programs, and false for static libs and header-only libs. '''
		try: return self._ld
		except AttributeError:
			if self.kind == ModTask.Kinds.HEADERS: self._ld = False
			elif self.kind == ModTask.Kinds.PROG: self._ld = True
			else: self._ld = self.cfg.shared
			return self._ld

	def __str__(self):
		if self.kind == ModTask.Kinds.HEADERS:
			if self.cxx_phase is not None: return 'deps of ' + str(self.cxx_phase)
			else: return 'deps of headers ' + self.name
		else: return 'deps of module ' + str(self.target)


	def do_mod_phase(self): pass

	class _ModPhaseCallbackTask(Task):
		def __init__(self, mod_task):
			Task.__init__(self)
			self.mod_task = mod_task

		def __str__(self):
			if self.mod_task.kind == ModTask.Kinds.HEADERS:
				if self.mod_task.cxx_phase is not None: return str(self.mod_task.cxx_phase)
				else: return 'install headers ' + self.mod_task.name
			else: return 'build module ' + str(self.mod_task.target)
		
		# Task
		def __call__(self, sched_ctx):
			for x in self.mod_task._mod_phase_callback(sched_ctx): yield x

	def _mod_phase_callback(self, sched_ctx):
		for x in sched_ctx.parallel_wait(self): yield x
		self.do_ensure_deps()

		# For static archives, we don't need to wait for the deps, but we want them to be done when the build finishes so that the resulting archive can be used.
		# For shared libs and programs, we need all deps before linking. We schedule them in advance, and don't wait for them right now, but just before linking.
		deep_deps = self._topologically_sorted_unique_deep_deps(expose_private_deep_deps=True)
		deep_deps_mod_phases = [dep.mod_phase for dep in deep_deps if dep.mod_phase is not None]
		sched_ctx.parallel_no_wait(*deep_deps_mod_phases)

		# We don't need the headers we export to clients, but we want clients to be able to use them.
		# We schedule the task but don't wait for it.
		if self.cxx_phase is not None: sched_ctx.parallel_no_wait(self.cxx_phase)

		# We need the headers of our deps.
		for x in self._do_deps_cxx_phases_and_apply_cxx_deep(sched_ctx): yield x

		if len(self.cfg.pkg_config) != 0:
			self.cfg.cxx_sig # compute the signature before, because we don't need pkg-config cxx flags in the cfg sig
			pkg_config_cxx_flags_task = _PkgConfigCxxFlagsTask.shared(self.cfg)
			for x in sched_ctx.parallel_wait(pkg_config_cxx_flags_task): yield x
			pkg_config_cxx_flags_task.apply_to(self.cfg)
			if self.ld:
				pkg_config_ld_flags_task = _PkgConfigLdFlagsTask.shared(self.cfg,
					# XXX pkg-config and static/shared (alternative is self.cfg.static_prog or not self.cfg.shared)
					expose_private_deep_deps=self.cfg.static_prog)
				sched_ctx.parallel_no_wait(pkg_config_ld_flags_task)

		self.do_mod_phase() # brings self.sources

		if __debug__ and is_debug and self.kind == ModTask.Kinds.HEADERS: assert len(self.sources) == 0

		try: old_pkg_config_sig, old_kind, old_ld, old_mod_sig, old_implicit_deps = self.persistent
		except KeyError:
			if __debug__ and is_debug: debug('task: no state: ' + str(self))
			old_pkg_config_sig, old_kind, old_ld, old_mod_sig, old_implicit_deps = self.persistent = None, None, None, None, {}
			self._type_changed = False
			changed_sources = self.sources
		else:
			self._type_changed = old_kind != self.kind or old_ld != self.ld
			if __debug__ and is_debug and self._type_changed: debug('task: mod type changed: ' + str(self))

			if self.kind != ModTask.Kinds.HEADERS:
				changed_sources = deque()
				if self.cfg.check_missing:
					self.obj_dir.lock.acquire()
					try:
						try: self.obj_dir.actual_children # not needed, just an optimisation
						except OSError: pass
					finally: self.obj_dir.lock.release()
				for s in self.sources:
					try: had_failed, old_cxx_sig, deps, old_dep_sig = old_implicit_deps[s]
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
						o = self.obj_dir / self._obj_name(s)
						if not o.exists:
							if __debug__ and is_debug: debug('task: target missing: ' + str(o))
							changed_sources.append(s)
							continue
					if __debug__ and is_debug: debug('task: skip: no change: ' + str(s))

		need_process = False

		if self.kind != ModTask.Kinds.HEADERS:
			# For shared libs and programs, we need all deps before linking.
			# So these are parts of the tasks we need to process before linking.
			tasks = self.ld and deep_deps_mod_phases or []

			if len(changed_sources) != 0:
				need_process = True
				batches = []
				for i in xrange(sched_ctx.thread_count): batches.append([])
				i = 0
				for s in changed_sources:
					batches[i].append(s)
					i = (i + 1) % sched_ctx.thread_count
				i = 0
				for b in batches:
					if len(b) == 0: break
					i += 1
					tasks.append(_BatchCompileTask(self, b))
				if not(__debug__ and is_debug) and not silent:
					color = color_bg_fg_rgb((0, 150, 180), (255, 255, 255))
					if self.cfg.pic: pic = 'pic'; color += ';1'
					else: pic = 'non-pic';
					s = [str(s) for s in changed_sources]
					s.sort()
					self.print_desc_multicolumn_format(str(self.target) + ': compiling ' + pic + ' objects from ' + self.cfg.lang + ' using ' + str(i) + ' processes and batch-size ' + str(len(batches[0])), s, color)
			elif self.cfg.check_missing:
				for t in self.targets:
					if not t.exists: # XXX If t.is_symlink we should check whether it points to something that exists.
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
				for dep in deep_deps: dep.apply_mod_to(self.cfg) # ordering matters for sig
				if not need_process:
					for dep in deep_deps:
						# When a dependant lib is a static archive, or changes its type from static to shared, we need to relink.
						# When the relink-on-shared-dep-impl-change option is on, we also relink to check that external symbols still exist.
						need_process = \
							isinstance(dep, ModTask) and dep.kind != ModTask.Kinds.HEADERS and \
							dep._needed_process and (not dep.ld or dep._type_changed or self.cfg.ld_on_shared_dep_impl_change)
						if need_process:
							if __debug__ and is_debug: debug('task: dep lib task changed: ' + str(self) + ' ' + str(dep))
							break
				if len(self.cfg.pkg_config) != 0:
					self.cfg.ld_sig # compute the signature before, because we don't need pkg-config ld flags in the cfg sig

			mod_sig = Sig(self.target_dir.abs_path)
			if self.kind != ModTask.Kinds.PROG and self.target_dir is not self.target_dev_dir:
				mod_sig.update(self.target_dev_dir.abs_path)
			if self.ld:
				mod_sig.update(self.cfg.ld_sig)
				if self.kind != ModTask.Kinds.PROG:
					mod_sig.update(str(self.version_interface), str(self.version_interface_min), str(self.version_impl))
			else: mod_sig.update(self.cfg.ar_ranlib_sig)
			mod_sig = mod_sig.digest()

			if old_mod_sig != mod_sig:
				if __debug__ and is_debug: debug('task: mod sig changed: ' + str(self))
				changed_sources = self.sources
				need_process = True
			elif not need_process:
				if len(old_implicit_deps) > len(self.sources):
					# Some source has been removed from the list of sources to build.
					if __debug__ and is_debug: debug('task: source removed: ' + str(self))
					need_process = True

			if not need_process:
				if __debug__ and is_debug: debug('task: skip: no change: ' + str(self))
			else:
				if self.ld and len(self.cfg.pkg_config) != 0:
						for x in sched_ctx.parallel_wait(pkg_config_ld_flags_task): yield x
						pkg_config_ld_flags_task.apply_to(self.cfg)
				self.target_dir.make_dir(self.target_dir)
				if self.kind != ModTask.Kinds.PROG and self.target_dir is not self.target_dev_dir: self.target_dev_dir.make_dir(self.target_dev_dir)
				sched_ctx.lock.release()
				try:
					if len(old_implicit_deps) == len(self.sources): # (yes this is correct, even if it looks strange)
						implicit_deps = old_implicit_deps
						removed_obj_names = None
					else:
						# remove old sources from implicit deps dictionary
						implicit_deps = {}
						for s in self.sources: implicit_deps[s] = old_implicit_deps[s]
						if self.ld: removed_obj_names = None
						else:
							# remove old objects from static archive
							removed_obj_names = []
							for s in old_implicit_deps:
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
						self.print_desc_multicolumn_format(str(self.target) + ': ' + desc + ' from objects', s, color)
					self.cfg.impl.process_mod_task(self, [self._obj_name(s) for s in sources], removed_obj_names)
					self.persistent = old_pkg_config_sig, self.kind, self.ld, mod_sig, implicit_deps
				finally: sched_ctx.lock.acquire()

		self._needed_process = need_process

		if not self.cfg.check_missing and (self.kind != ModTask.Kinds.HEADERS or self._type_changed): self.obj_dir.forget()

		for x in self._generate_pkg_config_file(sched_ctx): yield x

	def _generate_pkg_config_file(self, sched_ctx):
		if self.kind == ModTask.Kinds.PROG: return # could have some use too iirc on elf where programs can be used as libs?

		# Our BuildCfg is not the same as self.cfg.
		# It doesn't contain user-provided flags, nor expanded self.cfg.pkg_config flags.
		# It doesn't contain either what's been brought by deep mod tasks.
		cfg = BuildCfg(self.cfg.project)
		
		# copy impl settings
		cfg.lang = self.cfg.lang
		cfg.pic = self.cfg.pic
		cfg.shared = self.cfg.shared
		cfg.static_prog = self.cfg.static_prog
		cfg.impl = self.cfg.impl
		cfg.kind = self.cfg.kind
		cfg.version = self.cfg.version
		cfg.dest_platform = self.cfg.dest_platform
	
		self.apply_cxx_to(cfg)
		self.apply_mod_to(cfg)

		private_deps = self._topologically_sorted_unique_deep_deps(expose_private_deep_deps=True, expose_deep_mod_tasks=False)
		public_deps = self._topologically_sorted_unique_deep_deps(expose_private_deep_deps=False, expose_deep_mod_tasks=False)

		if False: # No need for the tasks to complete, because:
			# We just need to do apply_cxx_to and apply_mod_to.
			# While apply_cxx_to may use cxx_phase properties like dest_dir for an InstallTask cxx_phase,
			# e.g. def apply_cxx_to(self, cfg): cfg.include_paths.append(self.cxx_phase.dest_dir),
			# this can be done without the InstallTask cxx_phase having run.
			if not self.ld:
				# For shared libs and programs, we waited for all deps in _mod_phase_callback.
				# Otherwise, we need to wait for them here.
				for x in sched_ctx.parallel_wait(*(private_deps + public_deps)): yield x
		
		private_cfg = cfg.clone() # split between 'Libs' and 'Libs.private'
		for dep in private_deps:
			if isinstance(dep, ModTask): pass
			elif isinstance(dep, PkgConfigCheckTask): pass
			else: dep.apply_mod_to(private_cfg)
		for dep in public_deps:
			if isinstance(dep, ModTask): cfg.pkg_config.append(dep.name)
			elif isinstance(dep, PkgConfigCheckTask): cfg.pkg_config += dep.pkgs
			else: dep.apply_cxx_to(cfg); dep.apply_mod_to(cfg)

		need_process = False
		
		pkg_config_sig = Sig(
			self.title, self.description, self.version_string, self.url or '',
			cfg.fhs.prefix.abs_path, cfg.fhs.exec_prefix.abs_path, cfg.fhs.lib.abs_path, cfg.fhs.include.abs_path,
			cfg.cxx_sig, cfg.ld_sig
		)
		pkg_config_sig.update(*cfg.pkg_config)
		pkg_config_sig = pkg_config_sig.digest()

		# No need to check whether our persistent data exist since it has already been done in _mod_phase_callback.
		persistent = self.persistent

		if persistent[0] != pkg_config_sig:
			if __debug__ and is_debug: debug('task: pkg-config: sig changed: ' + str(self))
			need_process = True

		if need_process or self.cfg.check_missing:
			installed_pc_file = cfg.fhs.lib / 'pkgconfig' / (self.name + '.pc')
			uninstalled_pc_file = cfg.project.bld_dir / 'pkgconfig-uninstalled' / (self.name + '-uninstalled.pc')
			if self.cfg.check_missing:
				for f in (installed_pc_file, uninstalled_pc_file):
					f.parent.lock.acquire()
					try:
						try: f.parent.actual_children # not needed, just an optimisation
						except OSError: pass
					finally: f.parent.lock.release()
					if not f.exists:
						if __debug__ and is_debug: debug('task: pkg-config: file missing: ' + str(f))
						need_process = True
						break
		
		if need_process:
			sched_ctx.lock.release()
			try: 
				if not silent:
					if self.kind == ModTask.Kinds.HEADERS: desc = str(self.cxx_phase)
					else: desc = str(self.target)
					self.print_desc_multicolumn_format(desc + ': writing pkg-config files',
						[str(installed_pc_file), str(uninstalled_pc_file)], color_bg_fg_rgb((230, 100, 170), (255, 255, 255)) + ';1')
		
				def generate(uninstalled, file):
					# the 'prefix' variable is *mandatory* for proper working on MS-Windows; see pkg-config(1) manpage.
					prefix_dir = (uninstalled and cfg.fhs.prefix or cfg.fhs.dest.fs.root / cfg.fhs.prefix.rel_path(cfg.fhs.dest)).abs_path
					exec_prefix_dir = '${prefix}/' + cfg.fhs.exec_prefix.rel_path(cfg.fhs.prefix)
					lib_dir = '${exec_prefix}/' + cfg.fhs.lib.rel_path(cfg.fhs.exec_prefix)
					include_dir = '${prefix}/' + cfg.fhs.include.rel_path(cfg.fhs.prefix)

					cxx_flags = cfg.impl.client_cfg_cxx_args(cfg, '${includedir}')
					ld_flags = cfg.impl.client_cfg_ld_args(cfg, '${libdir}')
					private_ld_flags = cfg.impl.client_cfg_ld_args(private_cfg, '${libdir}')
					
					# Note that if the user specifies:
					# --install-dest-dir=/
					# --install-prefix-dir=/foo
					# --install-lib-dir=/bar
					#
					# we will end up with:
					#
					# prefix=/foo
					# exec_prefix=${prefix}/. (which expands to /foo/. )
					# libdir=${exec_prefix}/../bar (which expands to /foo/./../bar )
					#
					# While we could just use '/bar', a relative path is required for proper working on MS-Windows; see pkg-config(1) manpage.
					#
					# By comparison, autoconf, in our example, is not generating a path relative to ${prefix}, but just '/bar'.
					# With autoconf, the foobar.pc.in file would be:
					#
					# libdir=@libdir@
					#
					# With the default libdir, using the AC_CONFIG_FILES m4 macro the content of foobar.pc would become:
					#
					# libdir=${exec_prefix}/lib
					#
					# But as soon as the user gives a different value for the libdir variable, the relation with '${exec_prefix}' is lost.
					# For example, if the user invokes configure with:
					#
					# ../configure --libdir=/bar
					#
					# or invoke make with:
					#
					# make libdir=/bar
					#
					# the content of foobar.pc will become:
					#
					# libdir=/bar
					#
					# Autoconf-generated pkg-config files are hence not correct for windows, in that particular, far fetched case.
					#
					# PS: The autoconf manual http://www.gnu.org/s/hello/manual/autoconf/Installation-Directory-Variables.html says:
					# <quote>
					#    [...] you should not use these variables except in makefiles.
					#    [...] you should not rely on AC_CONFIG_FILES to replace bindir and friends in your shell scripts and other files.
					# </quote>
					#
					# Just like for makefiles, this is correct for pkg-config files because pkg-config does the recursive evaluation itself.
					# This doesn't work in the general case for foobar.sh shell scripts generated from from foobar.sh.in,
					# or for config headers generated by the AC_CONFIG_HEADERS m4 macro.
					#
					# The autoconf manual concludes that directory variables should be passed as '-D' compiler flags,
					# rather than attempting to put them in a config header.
					# See http://www.gnu.org/software/autoconf/manual/autoconf.html#Defining-Directories
					# This is only because AC_CONFIG_HEADERS is what i'd consider broken.
					# See for example the bugs is leads to and bad workarounds http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=370282
					# where they were trying to do recursive shell evals of the variables.
					#
					# The recommended way by the autoconf manual to achieve this is using makefile rules like these ones:
					#
					# foobar.sh: foobar.sh.in
					# foobar.sh: Makefile
					# \t         sed -e 's|@libdir@|$(libdir)|g' $@.in > $@
					#
					# Then the Makefile should have the variables:
					#
					# prefix=/foo
					# exec_prefix=${prefix}
					# libdir=${exec_prefix}/lib
					#
					# With automake, Makefile.am produces a Makefile.in, which contains these variable definitions:
					# prefix=@prefix@
					# exec_prefix=@exec_prefix@
					# libdir=@libdir@
					#
					# When autoconf processes the Makefile.in with the AC_CONFIG_FILES m4 macro to generate the Makefile,
					# we end up with:
					#
					# prefix=/foo
					# exec_prefix=${prefix}
					# libdir=${exec_prefix}/lib
					#
					# This is exactly what we mentionned before.
					
					s = \
						'# generated by wonderbuild' \
						'\n' \
						'\nprefix=' + prefix_dir + \
						'\nexec_prefix=' + exec_prefix_dir + \
						'\nlibdir=' + lib_dir + \
						'\nincludedir=' + include_dir + \
						'\n' \
						'\nName: ' + self.title + \
						'\nDescription: ' + self.description + \
						'\nVersion: ' + self.version_string
					if self.url: s += '\nURL: ' + self.url
					s += \
						'\nCflags: ' + ' '.join(cxx_flags) + \
						'\nLibs: ' + ' '.join(ld_flags) + \
						'\nLibs.private: ' + ' '.join(private_ld_flags) + \
						'\nRequires: ' + ' '.join(cfg.pkg_config)
					if False: s += '\nRequires.private: ...' # messy specification
					if False: s += '\nConflicts: ...'
					s += '\n'
					file.parent.make_dir(file.parent)
					f = open(file.path, 'w')
					try: f.write(s)
					finally: f.close()
					if __debug__ and is_debug:
						debug('task: pkg-config: wrote content of file ' + str(file) + '\n' + s + '---------- end of file ' + str(file))

				generate(False, installed_pc_file)
				generate(True, uninstalled_pc_file)
				self.persistent = pkg_config_sig, self.kind, self.ld, persistent[-2], persistent[-1]
			finally: sched_ctx.lock.acquire()

class _PkgConfigTask(CheckTask):

	@staticmethod
	def _shared_uid(class_, pkgs):
		pkgs.sort()
		return str(class_) + ' ' + ' '.join(pkgs)

	def __init__(self, persistent, uid, cfg, pkgs):
		CheckTask.__init__(self, persistent, uid, cfg.shared_checks)
		self.pkgs = pkgs

	@property
	def prog(self): return 'pkg-config'

	def __str__(self): return 'check pkg-config ' + ' '.join(self.what_args) + ' ' + ' '.join(self.pkgs)

	# CheckTask
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

	# CheckTask
	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			sig = self._sig = _PkgConfigTask.env_sig()
			return sig

	@staticmethod
	def env_sig():
		sig = Sig()
		for name in ('PKG_CONFIG_PATH', 'PKG_CONFIG_LIBDIR', 'PKG_CONFIG_DISABLE_UNINSTALLED'): # PKG_CONFIG_TOP_BUILD_DIR, PKG_CONFIG_ALLOW_SYSTEM_CFLAGS, PKG_CONFIG_ALLOW_SYSTEM_LIBS
			e = os.environ.get(name, None)
			if e is not None: sig.update(e)
		return sig.digest()

class _PkgConfigFlagsTask(_PkgConfigTask):

	def __init__(self, persistent, uid, cfg): _PkgConfigTask.__init__(self, persistent, uid, cfg, cfg.pkg_config)

	# _PkgConfigTask(CheckTask)
	def do_check_and_set_result(self, sched_ctx):
		if False: yield
		r, out, err = exec_subprocess_pipe(self.args, silent=True)
		if r != 0: raise Exception, r
		self.results = out.split()

	# _PkgConfigTask(CheckTask)
	if __debug__ and is_debug:
		@property
		def result_display(self): return ' '.join(self.result), ok_color
	else:
		@property
		def result_display(self): return 'ok', ok_color

	def apply_to(self): raise Exception, str(self.__class__) + ' did not redefine the method.'

class _PkgConfigCxxFlagsTask(_PkgConfigFlagsTask):

	# _PkgConfigFlagsTask(_PkgConfigTask(CheckTask(SharedTask)))
	@classmethod
	def shared_uid(class_, cfg): return _PkgConfigFlagsTask._shared_uid(class_, cfg.pkg_config)

	# _PkgConfigFlagsTask(_PkgConfigTask(CheckTask(SharedTask)))
	@classmethod
	def shared(class_, cfg): return _PkgConfigFlagsTask._shared(class_, cfg.shared_checks, cfg)

	# _PkgConfigFlagsTask(_PkgConfigTask)
	@property
	def what_desc(self): return 'cxx flags'
	
	# _PkgConfigFlagsTask(_PkgConfigTask)
	@property
	def what_args(self): return ['--cflags']

	# _PkgConfigFlagsTask
	def apply_to(self, cfg): cfg.cxx_flags += self.result

class _PkgConfigLdFlagsTask(_PkgConfigFlagsTask):

	# _PkgConfigFlagsTask(_PkgConfigTask(CheckTask(SharedTask)))
	@classmethod
	def shared_uid(class_, cfg, expose_private_deep_deps):
		uid = _PkgConfigFlagsTask._shared_uid(class_, cfg.pkg_config)
		if expose_private_deep_deps: uid += ' --static'
		return uid

	# _PkgConfigFlagsTask(_PkgConfigTask(CheckTask(SharedTask)))
	@classmethod
	def shared(class_, cfg, expose_private_deep_deps):
		return _PkgConfigFlagsTask._shared(class_, cfg.shared_checks, cfg, expose_private_deep_deps)

	def __init__(self, persistent, uid, cfg, expose_private_deep_deps):
		_PkgConfigFlagsTask.__init__(self, persistent, uid, cfg)
		self.expose_private_deep_deps = expose_private_deep_deps

	# _PkgConfigFlagsTask(_PkgConfigTask)
	@property
	def what_desc(self):
		if self.expose_private_deep_deps: return 'static ld flags'
		else: return 'shared ld flags'
	
	# _PkgConfigFlagsTask(_PkgConfigTask)
	@property
	def what_args(self):
		if self.expose_private_deep_deps: return ['--libs', '--static']
		else: return ['--libs']

	# _PkgConfigFlagsTask
	def apply_to(self, cfg): cfg.ld_flags += self.result

class PkgConfigCheckTask(_PkgConfigTask, ModDepPhases):

	# _PkgConfigTask(CheckTask(SharedTask))
	@classmethod
	def shared_uid(class_, cfg, pkgs): return _PkgConfigTask._shared_uid(class_, pkgs)

	# _PkgConfigTask(CheckTask(SharedTask))
	@classmethod
	def shared(class_, cfg, pkgs): return _PkgConfigTask._shared(class_, cfg.shared_checks, cfg, pkgs)

	def __init__(self, persistent, uid, cfg, pkgs):
		ModDepPhases.__init__(self)
		_PkgConfigTask.__init__(self, persistent, uid, cfg, pkgs)

	# ModDepPhases
	def apply_cxx_to(self, cfg): cfg.pkg_config += self.pkgs
		
	# _PkgConfigTask
	@property
	def what_desc(self): return 'existence'
	
	# _PkgConfigTask
	@property
	def what_args(self): return ['--exists']

	# _PkgConfigTask(CheckTask)
	# Note: This sets 'results', which indirectly sets the bool result property as defined in CheckTask.
	# The bool result is taken from CheckTask and not ModDepPhases because ModDepPhases comes last in the inheritance.
	def do_check_and_set_result(self, sched_ctx):
		if False: yield
		try: r = exec_subprocess(self.args)
		except Exception, e:
			if __debug__ and is_debug: debug('cfg: ' + self.desc + ': exception: ' + str(e))
			r = 1
		# note: in case of a positive result, we could as well store a positive result for each individual packages
		self.results = r == 0

class MultiBuildCheckTask(CheckTask, ModDepPhases):

	# CheckTask(SharedTask)
	@staticmethod
	def shared_uid(base_cfg, *args, **kw): raise Exception, str(MultiBuildCheckTask) + ' did not redefine the static method.'
	
	# CheckTask(SharedTask)
	@classmethod
	def shared(class_, base_cfg, *args, **kw): return CheckTask._shared(class_, base_cfg.shared_checks, base_cfg, *args, **kw)

	# CheckTask(SharedTask)
	@staticmethod
	def _shared(class_, base_cfg, *args, **kw): return CheckTask._shared(class_, base_cfg.shared_checks, *args, **kw)

	def __init__(self, persistent, uid, base_cfg, pipe_preproc=False, compile=True, link=True):
		CheckTask.__init__(self, persistent, uid, base_cfg.shared_checks)
		ModDepPhases.__init__(self)
		self.base_cfg = base_cfg
		self.pipe_preproc = pipe_preproc
		self.compile = compile
		self.link = link

	@property
	def cfg(self):
		try: return self._cfg
		except AttributeError:
			self._cfg = self.base_cfg.clone()
			if self.link: self.cfg.shared = False # build a program
			self.apply_cxx_to(self._cfg)
			self.apply_mod_to(self._cfg)
			return self._cfg

	@property
	def source_text(self): return '#error ' + str(self.__class__) + ' did not redefine default source text.\n'

	# CheckTask
	@property
	def sig(self):
		try: return self._sig
		except AttributeError:
			sig = Sig(self.source_text)
			sig.update(self.base_cfg.cxx_sig)
			if self.link: sig.update(self.base_cfg.ld_sig)
			sig = self._sig = sig.digest()
			return sig

class BuildCheckTask(MultiBuildCheckTask):
	@property
	def _prog_source_text(self):
		if self.pipe_preproc or not self.link: return self.source_text
		else: return self.source_text + '\nint main() { return 0; }\n'

	@property
	def bld_dir(self):
		try: return self._bld_dir
		except AttributeError:
			bld_dir = self.base_cfg.project.bld_dir
			bld_dir.lock.acquire()
			try: self._bld_dir = bld_dir / 'checks' / self.uid
			finally: bld_dir.lock.release()
			return self._bld_dir

	# MultiBuildCheckTask(CheckTask)
	def do_check_and_set_result(self, sched_ctx):
		if False: yield
		sched_ctx.lock.release()
		try:
			self.bld_dir.make_dir()
			r, out, err = self.cfg.impl.process_build_check_task(self)
			if 'recheck' in self.options: # no real need for a log file, the --verbose=exec option gives the same details
				log = self.bld_dir / 'build.log'
				f = open(log.path, 'w')
				try:
					f.write(self._prog_source_text); f.write('\n')
					f.write(str(self.cfg.cxx_args)); f.write('\n')
					f.write(str(self.cfg.ld_args)); f.write('\n')
					f.write(out); f.write('\n')
					f.write(err); f.write('\n')
					f.write('return code: '); f.write(str(r)); f.write('\n')
				finally: f.close()
			if self.pipe_preproc: self.results = r == 0, out
			else: self.results = r == 0
		finally: sched_ctx.lock.acquire()
