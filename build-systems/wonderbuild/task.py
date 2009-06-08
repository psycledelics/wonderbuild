#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

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

	def print_desc(self, desc, color = '7;1'):
		out.write(colored(color, 'wonderbuild: task: ' + desc) + '\n')
		#out.flush()
		
	def print_desc_multi_column_format(self, desc, list, color = '7;1'):
		desc = 'wonderbuild: task: ' + desc + ':'
		line = desc + ' ' + '  '.join(list)
		if len(line) > cols: line = desc + '\n\t' + '\n\t'.join(multi_column_formatting.format(list, cols - 8)) # less 8 because of the tab
		out.write(colored(color, line) + '\n')
		#out.flush()

class ProjectTask(Task):
	def __init__(self, project, *aliases): #XXX aliases as keyword
		Task.__init__(self)
		self.project = project
		project.add_task_aliases(self, *aliases)
	
	@property
	def uid(self): pass
	
	def _get_persistent(self): return self.project.persistent[self.uid]
	def _set_persistent(self, value): self.project.persistent[self.uid] = value
	persistent = property(_get_persistent, _set_persistent)
