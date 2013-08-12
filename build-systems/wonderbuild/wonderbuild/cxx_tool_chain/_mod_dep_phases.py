#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2007-2013 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from collections import deque

from wonderbuild import UserReadableException
from wonderbuild.logger import is_debug
from wonderbuild.task import Task

# mutual dependency
#from wonderbuild.cxx_tool_chain import ModTask

class ModDepPhases(object): # note: doesn't derive from Task, but derived classes must also derive from Task
	def __init__(self):
		if __debug__ and is_debug: assert isinstance(self, Task) # note: doesn't derive from Task, but derived classes must also derive from Task
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
			if self.result:
				all_deps = self.all_deps
				if len(all_deps) != 0:
					for x in sched_ctx.parallel_wait(*all_deps): yield x
					self.result = min(bool(dep) for dep in all_deps)

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
		from wonderbuild.cxx_tool_chain import ModTask
		expose_private_deps = expose_private_deep_deps or expose_deep_mod_tasks
		expose_private_deps_only = expose_private_deep_deps and not expose_deep_mod_tasks
		if expose_private_deep_deps: expose_private_deep_deps = None # called with True or False, but we use a tribool in the recursion
		result = deque(); seen = set() # ordering matters for sig, and static libs must appear after their clients
		def recurse(instance, root, expose_private_deps, expose_private_deep_deps, expose_deep_mod_tasks):
			if not root:
				if instance in seen: return
				seen.add(instance)
			for dep in expose_private_deps and (expose_private_deps_only and instance.private_deps or instance.all_deps) or instance.public_deps:
				if expose_deep_mod_tasks or not isinstance(dep, ModTask):
					if expose_private_deep_deps is None:
						recurse(dep, False,
							dep._expose_private_deep_deps, dep._expose_private_deep_deps and None,
							expose_deep_mod_tasks is not None and (expose_deep_mod_tasks or not isinstance(dep, ModTask) or None))
					else:
						recurse(dep, False,
							expose_private_deep_deps, expose_private_deep_deps,
							expose_deep_mod_tasks is not None and (expose_deep_mod_tasks or not isinstance(dep, ModTask) or None))
				elif not dep in seen:
						result.appendleft(dep)
						seen.add(dep)
			if not root: result.appendleft(instance)
		recurse(self, True, expose_private_deps, expose_private_deep_deps, expose_deep_mod_tasks)
		return result
