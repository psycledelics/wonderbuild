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
			self._scheduler = scheduler			
			self.thread_count = scheduler.thread_count
			self.lock = scheduler._lock

		def parallel(self, tasks): self._scheduler._parallel(tasks)
		def background(self, tasks): self._scheduler._background(tasks)
		def wait(self, tasks): self._scheduler._wait(tasks)

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
				task._queued = True
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
	
	def _thread_function(self, i):
		if __debug__ and is_debug: debug('sched: thread: ' + str(i) + ': started')
		self._condition.acquire()
		try:
			try:
				while True:
					while not self._done_or_break_condition() and len(self._task_queue) == 0: self._condition.wait(timeout = self.timeout)
					if self._done_or_break_condition(): break
					self._process_one(self._task_queue.pop())
					if self._done_condition():
						self._condition.notifyAll()
						break
			except StopIteration: pass
			except Exception, e:
				self.exception = e
				self._stop_requested = True
				self._condition.notifyAll()
				raise
		finally:
			if __debug__ and is_debug: debug('sched: thread: ' + str(i) + ': terminated')
			self._condition.release()

	def _done_condition(self): return self._joining and self._todo_count == 0
	
	def _done_or_break_condition(self): return self._done_condition() or self._stop_requested

	def _process_one(self, task):
		assert not task._processed
		if __debug__ and is_debug: debug('sched: processing task: ' + str(task))
		task(self._context)
		if __debug__ and is_debug: debug('sched: task processed: ' + str(task))
		task._processed = True
		self._todo_count -= 1
		self._condition.notifyAll()
			
	def _parallel(self, tasks):
		if __debug__ and is_debug: debug('sched: parallel tasks: ' + str([str(t) for t in tasks]))
		if len(tasks) != 1: self._background(tasks[1:])
		if tasks[0]._queued: self._wait(tasks)
		else:
			self._todo_count += 1
			tasks[0]._queued = True
			self._process_one(tasks[0])
			if len(tasks) != 1: self._wait(tasks[1:])
		if __debug__:
			for task in tasks: assert task._processed, task
	
	def _background(self, tasks):
		if __debug__ and is_debug: debug('sched: background tasks: ' + str([str(t) for t in tasks]))
		notify = 0
		for task in tasks:
			if not task._processed and not task._queued:
				self._task_queue.append(task)
				task._queued = True
				notify += 1
		if notify != 0:
			self._todo_count += notify
			self._condition.notify(notify)

	def _wait(self, tasks):
		if __debug__ and is_debug: debug('sched: waiting for tasks: ' + str([str(t) for t in tasks]))
		for task in tasks:
			while True:
				while not task._processed and not self._stop_requested and len(self._task_queue) == 0: self._condition.wait(timeout = self.timeout)
				if self._stop_requested: raise StopIteration
				if task._processed: break
				self._process_one(self._task_queue.pop())
		if __debug__:
			for task in tasks: assert task._processed, task
