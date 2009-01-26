#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from logger import out, colored

class Task(object):
	def __init__(self, project, aliases = None):
		self.project = project
		project.add_task_aliases(self, aliases)
		self.queued = False
		self.in_task_todo_count = 0
		self.out_tasks = []
		self.processed = False

	def __call__(self, sched_context):
		yield []
		raise StopIteration

	def print_desc(self, desc, color = '7;1'):
		out.write(colored(color, 'wonderbuild: task: ' + desc) + '\n')
		out.flush()
