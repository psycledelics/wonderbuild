#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2013-2015 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>


##############################################################################
#
# this script tests the @task decorator
#
##############################################################################


if __name__ == '__main__':
	import sys, os
	dir = os.path.dirname(__file__)
	sys.argv.append('--src-dir=' + dir)
	try: from wonderbuild.main import main
	except ImportError:
		dir = os.path.abspath(os.path.join(dir, os.pardir, os.pardir))
		if dir not in sys.path: sys.path.append(dir)
		try: from wonderbuild.main import main
		except ImportError:
			print >> sys.stderr, 'could not import wonderbuild module with path', sys.path
			sys.exit(1)
		else: main()
	else: main()

from wonderbuild.script import ScriptTask
from wonderbuild.task import task

class Wonderbuild(ScriptTask):
	def __call__(self, sched_ctx):
		print 'begin 0'
		for x in sched_ctx.parallel_wait(self.task1, self.task2): yield x
		print 'end 0'

	@task
	def task1(self, sched_ctx):
			print 'begin 1'
			for x in sched_ctx.parallel_wait(self.task3): yield x
			print 'end 1'

	@task
	def task2(self, sched_ctx):
			print 'begin 2'
			for x in sched_ctx.parallel_wait(self.task3): yield x
			print 'end 2'

	@task
	def task3(self, sched_ctx):
			print 'begin 3'
			if False: yield
			print 'end 3'
