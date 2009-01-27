#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2007-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os, threading

from logger import is_debug, debug, colored, silent
from options import options, known_options, help

try: cpu_count = os.sysconf('SC_NPROCESSORS_ONLN')
except: cpu_count = int(os.environ.get('NUMBER_OF_PROCESSORS', 1)) # env var defined on mswindows

known_options |= set(['--jobs=', '--timeout=', '--progress'])
help['--jobs='] = ('--jobs=<count>', 'use <count> threads in the scheduler to process the tasks', 'autodetected: ' + str(cpu_count))
help['--timeout='] = ('--timeout=<seconds>', 'wait at most <seconds> for a task to complete before considering it\'s busted', '3600.0')

class Scheduler(object):
	def __init__(self):
		self.thread_count = 0
		self.timeout = 0
		for o in options:
			if o.startswith('--jobs='): self.thread_count = int(o[len('--jobs='):])
			elif o.startswith('--timeout='): self.timeout = float(o[len('--timeout='):])
		if self.thread_count == 0: self.thread_count = cpu_count
		if self.timeout == 0: self.timeout = 3600.0

	class Context(object):
		def __init__(self, scheduler):
			self.thread_count = scheduler.thread_count
			self.lock = scheduler._lock

	def process(self, tasks):
		if self.thread_count == 1:
			self._lock = Scheduler._DummyLock()
			self._condition = Scheduler._DummyCondition()
			self._pre_start()
			self.add_tasks(tasks)
			self._joining = True
			self._thread_function(0) # XXX need a way to handle timeout
			self._post_join()
		else:
			self.start() # TODO add the tasks to the queue before starting all the threads
			self.add_tasks(tasks)
			self.join()
		
	class _DummyLock(object):
		def acquire(self): pass
		def release(self): pass
	
	class _DummyCondition(_DummyLock):
		def wait(self, timeout): pass
		def notify(self, count = 1): pass
		def notifyAll(self): pass

	def _pre_start(self):
		self._task_queue = []
		self._todo_count = 0
		self._stop_requested = self._joining = False
		self._context = Scheduler.Context(self)

	def start(self):
		if __debug__ and is_debug: debug('sched: starting threads: ' + str(self.thread_count))
		self._lock = threading.Lock()
		self._condition = threading.Condition(self._lock)
		self._pre_start()
		self._threads = []
		for i in xrange(self.thread_count):
			t = threading.Thread(target = self._thread_function, args = (i,), name = 'scheduler-thread-' + str(i))
			t.setDaemon(True)
			t.start()
			self._threads.append(t)

	def add_tasks(self, tasks):
		self._condition.acquire()
		try:
			notify = len(tasks)
			self._todo_count += notify
			self._task_queue += tasks
			for task in tasks:
				task.queued = True
				if __debug__ and is_debug: debug('sched: tasks queued ' + str(self._todo_count) + ' ' + str(len(self._task_queue)) + ' ' + str(task))
			self._condition.notify(notify)
		finally: self._condition.release()

	def stop(self):
		if __debug__ and is_debug: debug('sched: stopping threads')
		self._condition.acquire()
		try:
			self._stop_requested = True
			self._condition.notifyAll()
		finally: self._condition.release()
		self.join()
		
	def join(self):
		if __debug__ and is_debug: debug('sched: joining threads')
		self._condition.acquire()
		try:
			self._joining = True
			self._condition.notifyAll()
		finally: self._condition.release()
		for t in self._threads: t.join(timeout = self.timeout)
		del self._threads
		self._post_join()
	
	def _post_join(self):
		del self._condition
		del self._task_queue
		if hasattr(self, 'exception'): raise self.exception
	
	if __debug__:
		def _debug_state(self, i, event):
			debug(
				'sched: thread: ' + \
				str(i) + ': ' + \
				event + ': ' + \
				str(self._joining) + ' ' + \
				str(self._stop_requested) + ' ' + \
				str(self._todo_count) + ' ' + \
				str(len(self._task_queue)) + ' ' + \
				str(self._task_queue)
			)
			assert self._todo_count >= len(self._task_queue)
	
	def _thread_function(self, i):
		if __debug__ and is_debug: debug('sched: thread: ' + str(i) + ': started')
		self._condition.acquire()
		try:
			try:
				while True:
					while (not self._joining or self._todo_count != 0) and not self._stop_requested and len(self._task_queue) == 0:
						if __debug__ and is_debug: self._debug_state(i, 'waiting')
						self._condition.wait(timeout = self.timeout)
						if __debug__ and is_debug: self._debug_state(i, 'notified')
					if __debug__ and is_debug: self._debug_state(i, 'condition met')
					if self._joining and self._todo_count == 0 or self._stop_requested: break
					task = self._task_queue.pop()
					if __debug__ and is_debug: debug('sched: thread: ' + str(i) + ': task pop: ' + str(task) + ' ' + str(task.out_tasks))
					task.queued = False
					if not task.processed:
						task_gen = None
						try:
							try: task_gen = task.generator
							except AttributeError: task_gen = task.generator = task(self._context)
							in_tasks = task_gen.next()
						except StopIteration:
							if __debug__ and is_debug: debug('sched: thread: ' + str(i) + ': task processed: ' + str(task) + ' ' + str(task.out_tasks))
							task.processed = True
						except:
							if task_gen is not None:
								try: task_gen.close() # note: no close() on python 2.4
								except: pass # we only want the original exception
							raise
						else:
							notify = 0
							task.in_task_todo_count += len(in_tasks)
							for in_task in in_tasks:
								in_task.out_tasks.append(task)
								if not in_task.queued and in_task.in_task_todo_count == 0:
									if __debug__ and is_debug: debug('sched: thread: ' + str(i) + ': in task queued: ' + str(in_task))
									self._task_queue.append(in_task)
									in_task.queued = True
								 	notify += 1
							self._todo_count += notify
							if notify > 1: self._condition.notify(notify - 1)
							continue
					self._todo_count -= 1
					notify = -1
					for out_task in task.out_tasks:
						out_task.in_task_todo_count -= 1
						if not out_task.queued and out_task.in_task_todo_count == 0:
							if __debug__ and is_debug: debug('sched: thread: ' + str(i) + ': out task queued: ' + str(out_task))
							self._task_queue.append(out_task)
							out_task.queued = True
							notify += 1
					task.out_tasks = []
					if notify > 0: self._condition.notify(notify)
					elif notify < 0 and self._todo_count == 0 and self._joining:
						self._condition.notifyAll()
						break
			except Exception, e:
				self.exception = e
				self._stop_requested = True
				self._condition.notifyAll()
				raise
		finally:
			if __debug__ and is_debug: debug('sched: thread: ' + str(i) + ': terminated')
			self._condition.release()
