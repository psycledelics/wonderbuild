#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2007-2013 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os
from collections import deque

from wonderbuild.logger import is_debug, debug, color_bg_fg_rgb, silent
from wonderbuild.signature import Sig
from wonderbuild.task import Persistent, Task

from _mod_dep_phases import ModDepPhases
from _build_cfg import BuildCfg
from _pkg_config import PkgConfigCheckTask, PkgConfigCxxFlagsTask as _PkgConfigCxxFlagsTask, PkgConfigLdFlagsTask as _PkgConfigLdFlagsTask

_schedule_ahead = True

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
				if self.cfg.pic: pic = 'pic'
				else: pic = 'non-pic'; color += ';1'
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
			# Basically, a static lib must expose its private_deps for client linking.
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
		if _schedule_ahead:
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
				if _schedule_ahead: sched_ctx.parallel_no_wait(pkg_config_ld_flags_task)

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
					if self.cfg.pic: pic = 'pic'
					else: pic = 'non-pic'; color += ';1'
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
							if self.cfg.pic: pic = 'pic'
							else: pic = 'non-pic'; color += ';1'
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
		public_cfg = BuildCfg(self.cfg.project)
		
		# copy impl settings
		public_cfg.lang = self.cfg.lang
		public_cfg.pic = self.cfg.pic
		public_cfg.shared = self.cfg.shared
		public_cfg.static_prog = self.cfg.static_prog
		public_cfg.impl = self.cfg.impl
		public_cfg.kind = self.cfg.kind
		public_cfg.version = self.cfg.version
		public_cfg.dest_platform = self.cfg.dest_platform
	
		self.apply_cxx_to(public_cfg)
		private_cfg = public_cfg.clone() # split between 'Libs' and 'Libs.private'
		self.apply_mod_to(public_cfg)

		public_deps = self._topologically_sorted_unique_deep_deps(expose_private_deep_deps=False, expose_deep_mod_tasks=False)
		private_deps = self._topologically_sorted_unique_deep_deps(expose_private_deep_deps=True, expose_deep_mod_tasks=True, expose_private_deps_only=True)
		# Note: for private_deps we use expose_deep_mod_tasks=True, expose_private_deps_only=True.
		# This is because we avoid using Requires.private for private dependencies when we can instead use Libs.private.
		# Doing so means we need to flatten private deep ModTask dependencies directly into Libs.private.
		# For rationale, see comment in the code further below where the .pc file is written to.

		if False: # No need for the tasks to complete, because:
			# We just need to do apply_cxx_to and apply_mod_to.
			# While apply_cxx_to may use cxx_phase properties like dest_dir for an InstallTask cxx_phase,
			# e.g. def apply_cxx_to(self, cfg): cfg.include_paths.append(self.cxx_phase.dest_dir),
			# this can be done without the InstallTask cxx_phase having run.
			if not self.ld:
				# For shared libs and programs, we waited for all deps in _mod_phase_callback.
				# Otherwise, we need to wait for them here.
				for x in sched_ctx.parallel_wait(*(private_deps + public_deps)): yield x
		
		for dep in public_deps:
			if isinstance(dep, ModTask): public_cfg.pkg_config.append(dep.name)
			elif isinstance(dep, PkgConfigCheckTask): public_cfg.pkg_config += dep.pkgs
			else: dep.apply_cxx_to(public_cfg); dep.apply_mod_to(public_cfg)
		for dep in private_deps:
			if isinstance(dep, ModTask):
				# We avoid using Requires.private for private dependencies when we can instead use Libs.private.
				# For rationale, see comment in the code further below where the .pc file is written to.
				if False: private_cfg.pkg_config.append(dep.name) # uses Requires.private
				else: dep.apply_mod_to(private_cfg) # uses Libs.private
			elif isinstance(dep, PkgConfigCheckTask): private_cfg.pkg_config += dep.pkgs # uses Requires.private
			else: dep.apply_mod_to(private_cfg) # uses Libs.private

		need_process = False
		
		pkg_config_sig = Sig(
			self.title, self.description, self.version_string, self.url or '',
			self.cfg.fhs.prefix.abs_path, self.cfg.fhs.exec_prefix.abs_path, self.cfg.fhs.lib.abs_path, self.cfg.fhs.include.abs_path,
			public_cfg.cxx_sig, public_cfg.ld_sig,
			private_cfg.ld_sig
		)
		pkg_config_sig.update(*public_cfg.pkg_config)
		pkg_config_sig.update(*private_cfg.pkg_config)
		pkg_config_sig = pkg_config_sig.digest()

		# No need to check whether our persistent data exist since it has already been done in _mod_phase_callback.
		persistent = self.persistent

		if persistent[0] != pkg_config_sig:
			if __debug__ and is_debug: debug('task: pkg-config: sig changed: ' + str(self))
			need_process = True

		if need_process or self.cfg.check_missing:
			installed_pc_file = self.cfg.fhs.lib / 'pkgconfig' / (self.name + '.pc')
			uninstalled_pc_file = self.cfg.project.bld_dir / 'pkgconfig-uninstalled' / (self.name + '-uninstalled.pc')
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
						[str(installed_pc_file), str(uninstalled_pc_file)], color_bg_fg_rgb((230, 100, 170), (255, 255, 255)))
		
				def generate(uninstalled, file):
					# The 'prefix' variable is *mandatory* for proper working on MS-Windows; see pkg-config(1) manpage.
					# Currently, we use 3 more variables, 'exec_prefix', 'libdir' and 'includedir' whose values depend on that first 'prefix' variable.
					prefix_to_exec_prefix = self.cfg.fhs.exec_prefix.rel_path(self.cfg.fhs.prefix)
					if False: # long comment about autotools ...
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
						# See for example the bugs it leads to and bad workarounds http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=370282
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
						pass
					s = \
						'# generated by wonderbuild' \
						'\n' \
						'\nprefix=' + (uninstalled and self.cfg.fhs.prefix or self.cfg.fhs.dest.fs.root / self.cfg.fhs.prefix.rel_path(self.cfg.fhs.dest)).abs_path + \
						'\nexec_prefix=${prefix}' + (prefix_to_exec_prefix != os.curdir and '/' + prefix_to_exec_prefix or '') + \
						'\nlibdir=${exec_prefix}/' + self.cfg.fhs.lib.rel_path(self.cfg.fhs.exec_prefix) + \
						'\nincludedir=${prefix}/' + self.cfg.fhs.include.rel_path(self.cfg.fhs.prefix) + \
						'\n' \
						'\nName: ' + self.title + \
						'\nDescription: ' + self.description + \
						'\nVersion: ' + self.version_string
					if self.url: s += '\nURL: ' + self.url
					s += \
						'\nCFlags: ' + ' '.join(self.cfg.impl.client_cfg_cxx_args(public_cfg, '${includedir}')) + \
						'\nLibs: ' + ' '.join(self.cfg.impl.client_cfg_ld_args(public_cfg, '${libdir}')) + \
						'\nLibs.private: ' + ' '.join(self.cfg.impl.client_cfg_ld_args(private_cfg, '${libdir}')) + \
						'\nRequires: ' + ' '.join(public_cfg.pkg_config) + \
						'\nRequires.private: ' + ' '.join(private_cfg.pkg_config)
					if False: # long comment on Requires.private
						# Requires.private has two usages :
						#
						# - Case 1: public header-only dependency
						#   A public header of this package includes another package's header (so you need its CFlags),
						#   but this package's library does not directly call any code in the other package's library (so you don't want its Libs).
						#   So, pkg-config --cflags also brings indirect CFlags through Requires.private, whether you call it with --static or not,
						#   but when pkg-config is called *without* --static, pkg-config --libs doesn't bring indirect Libs.
						#   Note that this usage is *very* fragile; it may depend on the precise implementation of the other package's library:
						#   - Is that C++ class actually a POD type ?
						#   - Does it have a user-defined ctor, copy-ctor, move-ctor, dtor ?
						#   - If so, are they defined directly in the header ?
						#   - I'm calling inline functions only, but do these not call any non-inline ones themselves ?
						#   - Do I need RTTI ?
						#   - etc.
						#   Such dependency on code implementation details are to be handled at the compiler/linker level
						#   (linker's --as-needed flag, future C++ module ISO standard ...).
						#   In wonderbuild terms, this is neither a private nor a public dependency; it's inbetween.
						#   For the reasons mentionned above, wonderbuild will not add support such borderline usage;
						#   just use a public dependency and the linker shall do the job of eliminating unneeded references.
						#
						# - Case 2: --static
						#   When pkg-config is called with --static --libs, it *does* bring indirect Libs through Requires.private.
						#
						# Note that pkg-config is somewhat broken by design in the following common usage scenario:
						# - Case 3: private dependency
						#   You're not in case 1 (public header-only dependency),
						#   but rather using another package's code internally in this librarie's implementation.
						#   When pkg-config is called with --cflags, it *does* bring indirect CFlags through Requires.private,
						#   which, in this scenario (private dependency), are useless, but harmless.
						#   For this reason, wonderbuild avoids using Requires.private for private dependencies when it can instead use Libs.private.
						pass
					if False: s += '\nConflicts: ...'
					s += '\n'
					file.parent.make_dir(file.parent)
					f = open(file.path, 'w')
					try: f.write(s)
					finally: f.close()
					file.parent.lock.acquire()
					try: file.parent.actual_children[file.name] = file
					finally: file.parent.lock.release()
					if __debug__ and is_debug:
						debug('task: pkg-config: wrote content of file ' + str(file) + '\n' + s + '---------- end of file ' + str(file))

				generate(False, installed_pc_file)
				generate(True, uninstalled_pc_file)
				self.persistent = pkg_config_sig, self.kind, self.ld, persistent[-2], persistent[-1]
			finally: sched_ctx.lock.acquire()
