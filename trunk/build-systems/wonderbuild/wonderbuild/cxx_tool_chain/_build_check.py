#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2007-2013 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from wonderbuild.signature import Sig
from wonderbuild.check_task import CheckTask
from wonderbuild.cxx_tool_chain import ModDepPhases

class MultiBuildCheckTask(ModDepPhases, CheckTask):

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
		ModDepPhases.__init__(self)
		CheckTask.__init__(self, persistent, uid, base_cfg.shared_checks)
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

	# ModDepPhases(DepTask(Task)), CheckTask(DepTask(Task), SharedTask(Task))
	def __call__(self, sched_ctx):
		for x in ModDepPhases.__call__(self, sched_ctx): yield x
		for x in CheckTask.__call__(self, sched_ctx): yield x

	# CheckTask
	def do_check_and_set_result(self, sched_ctx):
		if False: yield x

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

	@property
	def return_code(self): return self._return_code

	@property		
	def out(self): return self._out

	@property		
	def err(self): return self._err

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
			if self.pipe_preproc: self._out = out
			self._return_code = r
			if r != 0: self._err = err
			self.result = r == 0
		finally: sched_ctx.lock.acquire()
