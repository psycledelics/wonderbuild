#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from logger import out, cols, colored
import multi_column_formatting

class Task(object):
	def __init__(self):
		self._queued = self._processed = False
	
	def __call__(self, sched_context): pass

	def print_desc(self, desc, color = '7;1'):
		out.write(colored(color, 'wonderbuild: task: ' + desc) + '\n')
		out.flush()
		
	def print_desc_multi_column_format(self, desc, list, color = '7;1'):
		desc = 'wonderbuild: task: ' + desc + ':'
		line = desc + ' ' + ' '.join(list)
		if len(line) > cols: line = desc + '\n\t' + '\n\t'.join(multi_column_formatting.format(list, cols - 8)) # less 8 because of the tab
		out.write(colored(color, line) + '\n')
		out.flush()
		
	def print_check(self, desc):
		out.write(colored('34', 'wonderbuild: task: ' + desc + ' ...') + '\n')
		out.flush()
		
	def print_check_result(self, desc, result, color):
		out.write(colored('34', 'wonderbuild: task: ' + desc + ': ') + colored(color, result) + '\n')
		out.flush()

class ProjectTask(Task):
	def __init__(self, project, *aliases):
		Task.__init__(self)
		self.project = project
		project.add_task_aliases(self, *aliases)
	
	@property
	def uid(self): pass
	
	def _get_persistent(self): return self.project.persistent[self.uid]
	def _set_persistent(self, value): self.project.persistent[self.uid] = value
	persistent = property(_get_persistent, _set_persistent)
