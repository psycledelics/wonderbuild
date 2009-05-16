#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from logger import is_debug, debug, silent, out, cols, colored
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

class CheckTask(ProjectTask):
	def __init__(self, project): ProjectTask.__init__(self, project)

	@property
	def sig(self): raise Exception, str(self.__class__) + ' did not redefine the property.'

	@property
	def uid(self): Exception, str(self.__class__) + ' did not redefine the property.'

	@property
	def desc(self): raise Exception, str(self.__class__) + ' did not redefine the method.'

	def do_check_and_set_result(self, sched_context): raise Exception, str(self.__class__) + ' did not redefine the method.'

	def __str__(self): return self.desc
	
	@property
	def result_display(self):
		if self.result: return 'yes', '32'
		else: return 'no', '31'

	def __call__(self, sched_context):
		try: old_sig, self._results = self.persistent
		except KeyError: old_sig = None
		if old_sig == self.sig:
			if __debug__ and is_debug: debug('task: skip: no change: ' + self.name)
		else:
			if not silent:
				desc = 'checking for ' + self.desc
				self.print_check(desc)
			self.do_check_and_set_result(sched_context)
			self.persistent = self.sig, self.results
			if not silent: self.print_check_result(desc, *self.result_display)

	@property
	def result(self): return self.results

	def _get_results(self):
		try: return self._results
		except AttributeError: raise Exception, 'did you forget to process the ' + str(self) + ' task?'
	def _set_results(self, value): self._results = value
	results = property(_get_results, _set_results)
