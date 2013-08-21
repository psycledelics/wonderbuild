#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2007-2013 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from wonderbuild.logger import is_debug, debug, color_bg_fg_rgb, silent
from wonderbuild.signature import Sig
from wonderbuild.task import Persistent, Task

from _mod_dep_phases import ModDepPhases
from _pkg_config import PkgConfigCxxFlagsTask as _PkgConfigCxxFlagsTask

class _PreCompileTask(ModDepPhases, Persistent):
	def __init__(self, name, base_cfg):
		ModDepPhases.__init__(self)
		Persistent.__init__(self, base_cfg.project.persistent, name)
		self.name = name
		self.base_cfg = base_cfg

	@property
	def cfg(self):
		try: return self._cfg
		except AttributeError:
			self._cfg = self.base_cfg.clone()
			return self._cfg
	
	# ModDepPhases
	def do_set_deps(self, sched_ctx):
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
		for x in self.ensure_deps(sched_ctx): yield x
		
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
					if self.cfg.pic: pic = 'pic'
					else: pic = 'non-pic'; color += ';1'
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

class PreCompileTasks(ModDepPhases): # XXX *NOT* to be used as a ModDepPhases ! One has to chose between .lib_task or .prog_task (pic vs non-pic)
	def __init__(self, name, base_cfg):
		ModDepPhases.__init__(self)
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

		# _PreCompileTask(ModDepPhases)
		def do_set_deps(self, sched_ctx):
			for x in sched_ctx.parallel_wait(self.parent_task): yield x
			self.private_deps = self.parent_task.private_deps
			self.public_deps = self.parent_task.public_deps
			try: self.parent_task.__cxx_phase_done
			except AttributeError:
				self.parent_task.do_cxx_phase()
				self.parent_task.__cxx_phase_done = True
			self.cfg.pic = self.pic # this clones the parent cfg and changes the pic setting
			for x in _PreCompileTask.do_set_deps(self, sched_ctx): yield x
	
	def do_cxx_phase(self): pass
