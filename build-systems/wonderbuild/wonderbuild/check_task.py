#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2010 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from option_cfg import OptionCfg
from task import SharedTask
from logger import out, colored, color_bg_fg_rgb, is_debug, debug, silent
import multi_column_formatting

ok_color = color_bg_fg_rgb((240, 255, 240), (0, 170, 0))
failed_color = color_bg_fg_rgb((255, 240, 240), (170, 0, 0))
_announce_color = color_bg_fg_rgb((240, 240, 255), (0, 0, 170))

class CheckTask(SharedTask, OptionCfg):

	# OptionCfg(OptionDecl)
	known_options = set(['recheck'])

	# OptionCfg(OptionDecl)
	@staticmethod
	def generate_option_help(help):
		help['recheck'] = ('[yes|no]', 'perform configuration checks again', 'no => do not recheck unless signature changed')

	def __init__(self, persistent, uid, shared_options_holder):
		SharedTask.__init__(self, persistent, uid)
		OptionCfg.__init__(self, shared_options_holder)

	@property
	def sig(self): raise Exception, str(self.__class__) + ' did not redefine the property.'

	def print_check(self, desc):
		if __debug__ and is_debug:
			out.write(colored(_announce_color, 'wonderbuild: task: checking for ' + desc + ' ...') + '\n')
			#out.flush()
	
	def print_check_result(self, desc, result, color):
		if __debug__ and is_debug:
			out.write(colored(_announce_color, 'wonderbuild: task: ... checked for ' + desc + ':') + ' ' + colored(color, result) + '\n')
		else:
			out.write(colored(_announce_color, 'wonderbuild: task: checked for ' + desc + ':') + ' ' + colored(color, result) + '\n')
		#out.flush()

	@property
	def desc(self): return self.uid

	def do_check_and_set_result(self, sched_ctx): raise Exception, str(self.__class__) + ' did not redefine the method.'

	def __str__(self): return 'check ' + self.desc

	@property
	def help(self): return str(self)
	
	@property
	def result_display(self):
		if self.result: return 'yes', ok_color
		else: return 'no', failed_color

	### the results vs result thing is to be removed

	@property
	def result(self): return self.results
	def __bool__(self): return self.result
	def __nonzero__(self): return self.__bool__() # __bool__ has become the default in python 3.0

	def _get_results(self):
		try: return self._results
		except AttributeError: raise Exception, 'did you forget to process the ' + str(self) + ' task?'
	def _set_results(self, value): self._results = value
	results = property(_get_results, _set_results)

	# SharedTask(Task)
	def __call__(self, sched_ctx):
		if 'recheck' not in self.options:
			try: old_sig, self._results = self.persistent
			except KeyError: pass
			else:
				if old_sig == self.sig:
					if __debug__ and is_debug: debug('task: skip: no change: ' + str(self))
					return
		if not silent:
			desc = self.desc
			self.print_check(desc)
		for x in self.do_check_and_set_result(sched_ctx): yield x
		self.persistent = self.sig, self.results
		if not silent: self.print_check_result(desc, *self.result_display)

	def help_package(self, search, url):
		s = \
			'For Debian-based distributions, use \'apt-cache search ' + search + '\' to look for the packages.\n' \
			'For Cygwin, use \'cygcheck --package-query ' + search + '\' to look for the packages.\n' \
			'If you don\'t find them in your distribution\'s packages, you may go to ' + url + ' .'
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
