#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2013 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from wonderbuild import UserReadableException
from wonderbuild.cxx_tool_chain import BuildCheckTask

class ValidCfgCheckTask(BuildCheckTask):
	'a check to simply test whether the user-provided compiler and linker flags are correct'

	# BuildCheckTask(MultiBuildCheckTask(CheckTask(SharedTask)))
	@staticmethod
	def shared_uid(*args, **kw): return 'valid-user-provided-build-cfg-flags'

	# BuildCheckTask(MultiBuildCheckTask)
	source_text = '' # the base class already adds a main() function

	def __call__(self, sched_ctx):
		# Don't do it all directly in do_check_and_set_result because it's not executed when sig hasn't changed.
		for x in BuildCheckTask.__call__(self, sched_ctx): yield x
		if not self: raise UserReadableException, str(self) + ': invalid user-provided build cfg flags:\n' + self.persistent_err

	# BuildCheckTask(CheckTask)
	def do_check_and_set_result(self, sched_ctx):
		for x in BuildCheckTask.do_check_and_set_result(self, sched_ctx): yield x
		self.result = self.result, not self.result and self.err or None

	def __bool__(self): return self.result[0]

	@property
	def persistent_err(self): return self.result[1]
