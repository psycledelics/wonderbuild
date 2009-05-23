#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from wonderbuild.task import ProjectTask
from logger import is_debug, debug, silent
import multi_column_formatting

class CheckTask(ProjectTask):
	@classmethod
	def shared(class_, *args, **kw):
		return class_(*args, **kw)
		# uid = str(class_)
		#try: instance = project.persistent[uid]
		#except KeyError: instance = project.persistent[uid] = class_(project, *args, **kw)
		#return instance
	
	def __init__(self, project): ProjectTask.__init__(self, project)

	@property
	def sig(self): raise Exception, str(self.__class__) + ' did not redefine the property.'

	@property
	def uid(self): Exception, str(self.__class__) + ' did not redefine the property.'

	@property
	def desc(self): raise Exception, str(self.__class__) + ' did not redefine the method.'

	def __str__(self): return self.desc

	@property
	def help(self): return str(self)
	
	def help_package(self, search, url):
		s = \
			'For Debian-based distributions, use \'apt-cache search ' + search + ' to look for the packages.\n' \
			'For Cygwin, use \'cygcheck --package-query ' + search + '\' to look for the packages.\n' \
			'If you don''t find them in your distribution\'s packages, you may go to ' + url + ' .'
		from wonderbuild.subprocess_wrapper import exec_subprocess_pipe
		for args in (
			('apt-cache', 'search', search),
			('cygcheck', '--package-query', search)
		):
			try: r, out, err = exec_subprocess_pipe(args, silent=True)
			except: pass
			else:
				if r == 0: s += \
					'\n\nResult of \'' + ' '.join(args) + \
					'\':\n\t' + '\n\t'.join(out.split('\n'))
		return s
	
	def do_check_and_set_result(self, sched_context): raise Exception, str(self.__class__) + ' did not redefine the method.'

	@property
	def result_display(self):
		if self.result: return 'yes', '32'
		else: return 'no', '31'

	def __call__(self, sched_context):
		try: old_sig, self._results = self.persistent
		except KeyError: old_sig = None
		if old_sig == self.sig:
			if __debug__ and is_debug: debug('task: skip: no change: ' + str(self))
		else:
			if not silent:
				desc = 'checking for ' + self.desc
				self.print_check(desc)
			self.do_check_and_set_result(sched_context)
			self.persistent = self.sig, self.results
			if not silent: self.print_check_result(desc, *self.result_display)

	@property
	def result(self): return self.results
	def __bool__(self): return self.result
	def __nonzero__(self): return self.result

	def _get_results(self):
		try: return self._results
		except AttributeError: raise Exception, 'did you forget to process the ' + str(self) + ' task?'
	def _set_results(self, value): self._results = value
	results = property(_get_results, _set_results)
