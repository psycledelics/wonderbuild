#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2009-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>


##############################################################################
#
# this script simply builds all of the tests
#
##############################################################################


if __name__ == '__main__':
	import sys, os
	dir = os.path.dirname(__file__)
	sys.argv.append('--src-dir=' + dir)
	try: from wonderbuild.main import main
	except ImportError:
		dir = os.path.abspath(os.path.join(dir, os.pardir))
		if dir not in sys.path: sys.path.append(dir)
		try: from wonderbuild.main import main
		except ImportError:
			print >> sys.stderr, 'could not find wonderbuild'
			sys.exit(1)
		else: main()
	else: main()

else:
	from wonderbuild.script import ScriptTask, ScriptLoaderTask

	class Wonderbuild(ScriptTask):
		def __call__(self, sched_ctx):
			for x in sched_ctx.parallel_wait(
				*(
					ScriptLoaderTask.shared(self.project, self.src_dir / dir) \
					for dir in (
						'static-shared',
						'pre-compiled'
					)
				)
			): yield x
			
			if False:
				project = self.project
				from wonderbuild.task import Task
				class Foo(Task):
					@staticmethod
					def shared(hold, x0, x1, y):
						try: x0s = hold.foos
						except AttributeError: x0s = hold.foos = {}
						try: x1s = x0s[x0]
						except KeyError: x1s = x0s[x0] = {}
						try: foos = x1s[x1]
						except KeyError: foos = x1s[x1] = {}
						try: return foos[y]
						except KeyError:
							foo = foos[y] = Foo(x0, x1, y)
							return foo
			
					def __init__(self, x0, x1, y):
						Task.__init__(self)
						self.x0 = x0
						self.x1 = x1
						self.y = y
					def __call__(self, sched_ctx):
						sched_ctx.lock.release() # allow parallelism
						try:
							x0, x1, y = self.x0, self.x1, self.y
							if x1 - x0 > 100:
								x = (x0 + x1) // 2
								tasks = Foo.shared(project, x0, x, y), Foo.shared(project, x, x1, y)
								sched_ctx.lock.acquire() # we need to reacquire the lock before yielding back into the scheduler
								try:
									for x in sched_ctx.parallel_wait(*tasks): yield x
								finally: sched_ctx.lock.release()
								self.result = tasks[0].result + tasks[1].result
							else:
								self.result = []
								for x in xrange(x0, x1): self.result.append(x * y)
						finally: sched_ctx.lock.acquire()

				f1 = Foo.shared(project, 0, 2000, 2)
				f2 = Foo.shared(project, 1000, 3000, 2)
				for x in sched_ctx.parallel_wait(f1, f2): yield x
				print f1.result, f2.result

