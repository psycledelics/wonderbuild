#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2010 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from logger import is_debug, debug, out, cols, colored, multicolumn_format

if False:
	# TODO @task decorator : allow tasks directly on functions
	# TODO This would also speed up attributes in filesystem.py
	class cache(object):
		'''Computes attribute value and caches it in the instance.
		Python Cookbook (Denis Otkidach) http://stackoverflow.com/users/168352/denis-otkidach
		This decorator allows you to create a property which can be computed once and
		accessed many times. Sort of like memoization.

		'''
		def __init__(self, method, name=None):
			# record the unbound-method and the name
			self.method = method
			self.name = name or method.__name__
			self.__doc__ = method.__doc__
		def __get__(self, inst, cls):
			# self: <__main__.cache object at 0xb781340c>
			# inst: <__main__.Foo object at 0xb781348c>
			# cls: <class '__main__.Foo'>       
			if inst is None:
				# instance attribute accessed on class, return self
				# You get here if you write `Foo.bar`
				return self
			# compute, cache and return the instance's attribute value
			result = self.method(inst)
			# setattr redefines the instance's attribute so this doesn't get called again
			setattr(inst, self.name, result)
			return result

class Task(object):

	if False: # This is now done lazily directly in the Scheduler.
		def __init__(self):
			self._sched_stacked = task._sched_processed = False
			self._sched_in_task_todo_count = 0
			self._sched_out_tasks = []

	def __call__(self, sched_ctx):
		if False: yield
		# example:
		#
		# for x in (sub_task_1, sub_task_2, ...): yield x
		#
		# sched_ctx.release()
		# try: do something
		# finally: sched_ctx.acquire()
		#
		# for x in (more_sub_task_1, more_sub_task_2, ...): yield x
		#
		# sched_ctx.release()
		# try: do something more
		# finally: sched_ctx.acquire()
		#
		# for x in (again_more_sub_task_1, again_more_sub_task_2, ...): yield x

	@staticmethod
	def print_desc(desc, color='7;1'):
		out.write(colored(color, 'wonderbuild: task: ' + desc) + '\n')
		
	@staticmethod
	def print_desc_multicolumn_format(desc, list, color = '7;1'):
		desc = 'wonderbuild: task: ' + desc + ':'
		if cols == 0: out.write(colored(color, desc) + '\n  ' + '\n  '.join(list) + '\n')
		else:
			joined_list = '  '.join(list)
			if len(desc) + 1 + len(joined_list) <= cols: out.write(colored(color, desc) + ' ' + joined_list + '\n')
			elif len(desc) % cols + 1 + len(joined_list) <= cols:
				s = ''
				i = 0
				while True:
					s += colored(color, desc[i : i + cols])
					i += cols
					if i < len(desc): s += '\n'
					else: break
				s += ' ' + joined_list + '\n'
				out.write(s)
			else:
				s = ''
				i = 0
				while True:
					s += colored(color, desc[i : i + cols])
					i += cols
					if i < len(desc): s += '\n'
					else: break
				s += '\n'
				indent = '  '
				for line in multicolumn_format(list, cols - len(indent)):
					s += indent + line + '\n'
				out.write(s)

class PurgeablePersistentDict(dict):

	# TODO Without this, fs global_purge_unused_children cannot reliably purge fs nodes since (old) tasks' persistent data will still reference deleted nodes.
	# TODO Then doing node1.rel_path(node2), where node1 and node2 don't have a common ancestor *instance*, will return node1's abs_path.
	# TODO If you then do node3 / abs_path, you still get node1, which is not expected!
	# TODO This badly breaks the install tasks that wants to remove in dest dir, node3 in that example, and instead removes node1, the original source!
	# TODO For now, fs global_purge_unused_children is entirely disabled. Only the safe fs partial_purge_unused_children is used.
	# TODO This is not top priority because it's only useful after some tasks have been removed or renamed in the user build scripts,
	# TODO and we want to trim their ghost signatures from the pickle. The pickle file won't grow fat unless the user build script change.
	def purge(self): pass

class Persistent(object):

	def __init__(self, persistent_dict, uid):
		self._persistent_dict = persistent_dict
		self.uid = uid

	def _get_persistent(self): return self._persistent_dict[self.uid]
	def _set_persistent(self, value): self._persistent_dict[self.uid] = value
	persistent = property(_get_persistent, _set_persistent)

class SharedTaskHolder(object): # Note: Currently the only use is the derived class Project.

	def __init__(self, persistent, options, option_collector, bld_dir):
		self.persistent = persistent
		self.options = options
		self.option_collector = option_collector
		self.bld_dir = bld_dir
		self._shared_tasks = {}

class SharedTask(Task, Persistent): # Note: Currently the only use is the derived class CheckTask.
		
	@classmethod
	def shared_uid(class_, *args, **kw): raise Exception, str(class_) + ' did not redefine the class method.'

	@classmethod
	def shared(class_, holder, *args, **kw): return SharedTask._shared(class_, holder, *args, **kw)

	@staticmethod
	def _shared(class_, holder, *args, **kw):
		uid = class_.shared_uid(*args, **kw)
		try: instance = holder._shared_tasks[uid]
		except KeyError: instance = holder._shared_tasks[uid] = class_(holder.persistent, uid, *args, **kw)
		return instance
	
	def __init__(self, persistent_dict, uid):
		Task.__init__(self)
		Persistent.__init__(self, persistent_dict, uid)
