#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from logger import out, colored

class Task(object):
	def __init__(self, project, aliases = None):
		self.project = project
		project.add_task_aliases(self, aliases)
		self._queued = self._processed = False

	def __call__(self, sched_context): pass

	def print_desc(self, desc, color = '7;1'):
		out.write(colored(color, 'wonderbuild: task: ' + desc) + '\n')
		out.flush()
		
	def print_check(self, desc):
		out.write(colored('34', 'wonderbuild: cfg: ' + desc + ' ...') + '\n')
		out.flush()
		
	def print_check_result(self, desc, result, color):
		out.write(colored('34', 'wonderbuild: cfg: ' + desc + ': ') + colored(color, result) + '\n')
		out.flush()
