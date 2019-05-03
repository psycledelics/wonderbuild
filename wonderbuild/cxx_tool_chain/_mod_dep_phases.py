#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2007-2013 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from collections import deque

from wonderbuild import UserReadableException
from wonderbuild.logger import is_debug
from wonderbuild.check_task import DepTask

# mutual dependency
#from wonderbuild.cxx_tool_chain import ModTask

class ModDepPhases(DepTask):
	def __init__(self):
		DepTask.__init__(self)
		self.private_deps = [] # of ModDepPhases
		self.public_deps = [] # of ModDepPhases
		self.cxx_phase = self.mod_phase = None

	@property
	def all_deps(self): return self.public_deps + self.private_deps

	# DepTask(Task)
	def __call__(self, sched_ctx):
		for x in self.do_set_deps(sched_ctx): yield x
		all_deps = self.all_deps
		if len(all_deps) == 0: self.result = True
		else:
			for x in sched_ctx.parallel_wait(*all_deps): yield x
			self.result = min(bool(d) for d in all_deps)

	def do_set_deps(self, sched_ctx):
		if False: yield

	def ensure_deps(self, sched_ctx):
		if not self:
			def dep_desc(instance): return str(instance.mod_phase or instance.cxx_phase or instance)
			def dep_help(instance): return instance.help or dep_desc(instance)
			all_deps = self.all_deps
			if len(all_deps) == 0:
				raise UserReadableException, dep_help(self)
			else:
				for dep in all_deps:
					if not dep:
						desc = 'unmet dependency:\n' + dep_desc(self) + '\nhas an unmet dependency on:\n'
						try:
							for x in dep.ensure_deps(sched_ctx): yield x
						except UserReadableException, e:
							# XXX ugly!
							ugly1 = dep_desc(dep)
							ugly2 = str(e)
							if ugly1 != ugly2: desc += ugly1 + ',\n... chained from ... ' + ugly2
							else: desc += ugly1
						else: desc += dep_desc(dep)
						raise UserReadableException, desc
		if __debug__ and is_debug: assert self

	def apply_cxx_to(self, cfg): pass
	def apply_mod_to(self, cfg): pass
	
	def _do_deps_cxx_phases_and_apply_cxx_deep(self, sched_ctx):
		deep_deps = self._topologically_sorted_unique_deep_deps(expose_private_deep_deps=False)
		cxx_phases = (dep.cxx_phase for dep in deep_deps if dep.cxx_phase is not None)
		for x in sched_ctx.parallel_wait(*cxx_phases): yield x
		for dep in deep_deps: dep.apply_cxx_to(self.cfg) # ordering matters for sig

 	@property
	def _expose_private_deep_deps(self): return False

	def _topologically_sorted_unique_deep_deps(self, expose_private_deep_deps, expose_deep_mod_tasks=True, expose_private_deps_only=False):
		# TODO I think it's boggus. See wondermake for a fix
		from wonderbuild.cxx_tool_chain import ModTask
		result = deque(); seen = set() # ordering matters for sig, and static libs must appear after their clients
		def recurse(instance, root, expose_private_deps, expose_private_deep_deps, expose_deep_mod_tasks):
			if not root:
				if instance in seen: return
				seen.add(instance)
			for dep in expose_private_deps and (expose_private_deps_only and instance.private_deps or instance.all_deps) or instance.public_deps:
				# Only ModTasks may depend on ModTasks, i.e., non-ModTasks never depend on ModTasks.
				# So we can optimise-out the check in the recursion.
				dep_expose_deep_mod_tasks = expose_deep_mod_tasks or not isinstance(dep, ModTask)
				if dep_expose_deep_mod_tasks:
					if expose_private_deep_deps is None:
						recurse(dep, False,
							dep._expose_private_deep_deps, dep._expose_private_deep_deps and None,
							dep_expose_deep_mod_tasks)
					else:
						recurse(dep, False,
							expose_private_deep_deps, expose_private_deep_deps,
							dep_expose_deep_mod_tasks)
				elif not dep in seen:
					result.appendleft(dep)
					seen.add(dep)
			if not root: result.appendleft(instance)
		recurse(self, True,
			expose_private_deep_deps or expose_deep_mod_tasks, expose_private_deep_deps and None, # called with True or False, but we use a tribool in the recursion
			expose_deep_mod_tasks)
		return result
