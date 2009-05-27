#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2007-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os, threading
from collections import deque

from wonderbuild import UserReadableException
from logger import is_debug, debug, colored, silent

try: cpu_count = os.sysconf('SC_NPROCESSORS_ONLN')
except: cpu_count = int(os.environ.get('NUMBER_OF_PROCESSORS', 1)) # env var defined on mswindows

_default_timeout = 3600.0

class Scheduler(object):
	known_options = set(['jobs', 'timeout'])

	@staticmethod
	def generate_option_help(help):
		help['jobs'] = ('<count>', 'use <count> threads in the scheduler to process the tasks', 'autodetected: ' + str(cpu_count))
		help['timeout'] = ('<seconds>', 'wait at most <seconds> for a task to complete before considering it\'s busted', str(_default_timeout))

	def __init__(self, options):
		self.thread_count = int(options.get('jobs', cpu_count))
		self.timeout = float(options.get('timeout', _default_timeout))

	class Context(object):
		def __init__(self, scheduler):
			self.thread_count = scheduler.thread_count
			self.lock = scheduler._lock
			self.parallel_wait = scheduler._parallel_wait
			self.parallel_no_wait = scheduler._parallel_no_wait
			self.wait = scheduler._wait

	class _DummyLock(object):
		def acquire(self): pass
		def release(self): pass
	
	class _DummyCondition(_DummyLock):
		def wait(self, timeout): pass
		def notify(self, count = 1): pass
		def notifyAll(self): pass

	def process(self, *tasks):
		self._task_queue = deque(tasks)
		self._todo_count = len(tasks)
		for task in tasks:
			task._queued = True
			if __debug__ and is_debug: debug('sched: tasks queued ' + str(self._todo_count) + ' ' + str(len(self._task_queue)) + ' ' + str(task))

		if self.thread_count == 1:
			self._lock = Scheduler._DummyLock()
			self._condition = Scheduler._DummyCondition()
		else:
			self._lock = threading.Lock()
			self._condition = threading.Condition(self._lock)
		self._context = Scheduler.Context(self)

		self._stop_requested = False

		if self.thread_count != 1:
			if __debug__ and is_debug: debug('sched: starting threads: ' + str(self.thread_count))
			#sys.setcheckinterval(interval)
			self._joining = False
			self._threads = []
			remaining_start_count = self.thread_count - 1
			remaining_start_condition = threading.Condition(threading.Lock())
			remaining_start_condition.acquire()
			try:
				t = threading.Thread(target = self._thread_loop, args = (0, remaining_start_count - 1, remaining_start_condition), name = 'scheduler-thread-' + str(0))
				t.setDaemon(True)
				t.start()
				self._threads.append(t)
				while len(self._threads) != remaining_start_count: remaining_start_condition.wait(timeout = self.timeout)
			finally: remaining_start_condition.release()

		self._joining = True
		try: self._thread_loop(-1, 0, None) # note: no timeout handling here
		finally:
			if self.thread_count != 1:
				if __debug__ and is_debug: debug('sched: joining threads')
				self._condition.acquire()
				try:
					self._joining = True
					self._condition.notifyAll()
				finally: self._condition.release()
				for t in self._threads: t.join(timeout = self.timeout)
			if hasattr(self, 'exception'):
				if isinstance(self.exception, UserReadableException): raise self.exception
				else: raise UserReadableException, 'An exception occurred, see stack trace above.'
		
	def _thread_loop(self, i, remaining_start_count, remaining_start_condition):
		if __debug__ and is_debug: debug('sched: thread: ' + str(i) + ': started')
		if remaining_start_condition is not None:
			remaining_start_condition.acquire()
			try:
				if remaining_start_count == 0: remaining_start_condition.notify()
				else:
					t = threading.Thread(target = self._thread_loop, args = (i + 1, remaining_start_count - 1, remaining_start_condition), name = 'scheduler-thread-' + str(i + 1))
					t.setDaemon(True)
					t.start()
					self._threads.append(t)
			finally: remaining_start_condition.release()
		self._condition.acquire()
		try:
			try:
				while True:
					while not self._done_or_break_condition() and len(self._task_queue) == 0: self._condition.wait(timeout = self.timeout)
					if self._done_or_break_condition(): break
					self._process_one_task(self._task_queue.pop())
					if self._done_condition():
						self._condition.notifyAll()
						break
			except StopIteration: pass
			except Exception, e:
				self.exception = e
				self._stop_requested = True
				self._condition.notifyAll()
				if not isinstance(e, UserReadableException):
					import traceback
					traceback.print_exc()
		finally:
			if __debug__ and is_debug: debug('sched: thread: ' + str(i) + ': terminated')
			self._condition.release()

	def _done_condition(self): return self._joining and self._todo_count == 0
	
	def _done_or_break_condition(self): return self._done_condition() or self._stop_requested

	def _process_one_task(self, task):
		if __debug__ and is_debug:
			debug('sched: processing task: ' + str(task))
			assert not task._processed

		task(self._context)
		#try: task(self._context)
		#except Exception, e: raise Exception, '\nin task: ' + str(task) + ': ' + str(e)

		if __debug__ and is_debug: debug('sched: task processed: ' + str(task))
		task._processed = True
		self._todo_count -= 1
		self._condition.notifyAll()
	
	def _parallel_wait(self, *tasks):
		if __debug__ and is_debug: debug('sched: parallel_wait: ' + str([str(t) for t in tasks]))
		count = len(tasks)
		if count == 0: return
		if count != 1: self._parallel_no_wait(*tasks[1:])
		if tasks[0]._queued: self._wait(*tasks)
		else:
			self._todo_count += 1
			tasks[0]._queued = True
			self._process_one_task(tasks[0])
			if count != 1: self._wait(*tasks[1:])
		if __debug__ and is_debug:
			for task in tasks: assert task._processed, task
	
	def _parallel_no_wait(self, *tasks):
		if __debug__ and is_debug: debug('sched: parallel_no_wait: ' + str([str(t) for t in tasks]))
		notify = 0
		for task in tasks:
			if not task._processed and not task._queued:
				self._task_queue.appendleft(task)
				task._queued = True
				notify += 1
		if notify != 0:
			self._todo_count += notify
			self._condition.notify(notify)

	def _wait(self, *tasks):
		if __debug__ and is_debug: debug('sched: waiting for tasks: ' + str([str(t) for t in tasks]))
		for task in tasks:
			while True:
				while not task._processed and not self._stop_requested and len(self._task_queue) == 0: self._condition.wait(timeout = self.timeout)
				if self._stop_requested: raise StopIteration
				if task._processed: break
				self._process_one_task(self._task_queue.pop())
		if __debug__ and is_debug:
			for task in tasks: assert task._processed, task
