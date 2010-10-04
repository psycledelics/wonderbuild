#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2010 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from logger import is_debug, debug, out, cols, colored
import multi_column_formatting

class Task(object):

	def __init__(self):
		self._sched_stacked = self._sched_processed = False
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

	def print_desc(self, desc, color='7;1'):
		out.write(colored(color, 'wonderbuild: task: ' + desc) + '\n')
		
	def print_desc_multi_column_format(self, desc, list, color = '7;1'):
		desc = 'wonderbuild: task: ' + desc + ':'
		joined_list = '  '.join(list)
		if len(desc) + 1 + len(joined_list) <= cols: out.write(colored(color, desc) + ' ' + joined_list + '\n')
		else:
			lines = [colored(color, desc)]
			indent = ' ' * 2
			for line in multi_column_formatting.format(list, cols - len(indent)):
				lines.append(indent + line)
			lines.append('')
			out.write('\n'.join(lines))

class PersistentDict(dict):

	def purge(self): pass # TODO

class Persistent(object):

	def __init__(self, persistent_dict, uid):
		self._persistent_dict = persistent_dict
		self.uid = uid

	def _get_persistent(self): return self._persistent_dict[self.uid]
	def _set_persistent(self, value): self._persistent_dict[self.uid] = value
	persistent = property(_get_persistent, _set_persistent)

class SharedTaskHolder(object):

	def __init__(self, persistent, options, option_collector, bld_dir):
		self.persistent = persistent
		self.options = options
		self.option_collector = option_collector
		self.bld_dir = bld_dir
		self._shared_tasks = {}

class SharedTask(Task, Persistent):
		
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
	
	def __init__(self, persistent, uid):
		Task.__init__(self)
		Persistent.__init__(self, persistent, uid)

class ProjectTask(Task):

	def __init__(self, project, aliases=None):
		Task.__init__(self)
		self.project = project
		if aliases is not None: project.add_task_aliases(self, *aliases)

