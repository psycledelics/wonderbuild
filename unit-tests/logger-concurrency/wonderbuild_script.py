#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2013-2015 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>


##############################################################################
#
# this script tests the logger's concurrency
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
from wonderbuild.subprocess_wrapper import exec_subprocess

class Wonderbuild(ScriptTask):

	@task
	def foo(self, sched_ctx):
		if False: yield
		for i in xrange(3):
			sched_ctx.lock.release()
			try: exec_subprocess(['sh', '-c', "for i in 1 2; do echo -n %s.$i f; sleep 1; echo -n o; sleep 1; echo o; done" % i])
			finally: sched_ctx.lock.acquire()

	@task
	def bar(self, sched_ctx):
		if False: yield
		for i in xrange(3):
			sched_ctx.lock.release()
			try: exec_subprocess(['sh', '-c', "for i in 1 2 3; do echo -n %s.$i b; sleep 1; echo -n a; sleep 1; echo r; done" % i])
			finally: sched_ctx.lock.acquire()

	@task
	def xyz(self, sched_ctx):
		if False: yield
		for i in xrange(3):
			sched_ctx.lock.release()
			try: exec_subprocess(['sh', '-c', "for i in 1 2 3 4; do echo -n %s.$i x; sleep 1; echo -n y; sleep 1; echo z; done" % i])
			finally: sched_ctx.lock.acquire()

	def __call__(self, sched_ctx):
		for x in sched_ctx.parallel_wait(self.foo, self.bar, self.xyz): yield x

