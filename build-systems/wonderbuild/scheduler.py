#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2007-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os, threading

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
		self._task_stack = list(tasks)
		self._todo_count = len(tasks)
		for task in tasks:
			task._sched_stacked = True
			if __debug__ and is_debug: debug('sched: tasks stacked ' + str(self._todo_count) + ' ' + str(len(self._task_stack)) + ' ' + str(task))

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
						while not self._done_or_break_condition() and len(self._task_stack) == 0:
							if __debug__ and is_debug: debug('sched: thread: ' + str(i) + ': waiting')
							self._condition.wait(timeout = self.timeout)
							if __debug__ and is_debug: debug('sched: thread: ' + str(i) + ': notified')
						if __debug__ and is_debug: debug('sched: thread: ' + str(i) + ': condition met')
						if self._done_or_break_condition(): break
						task = self._task_stack.pop()
						if __debug__ and is_debug: debug('sched: thread: ' + str(i) + ': task pop: ' + str(task) + ' ' + str(task.out_tasks))
						if not task._sched_processed:
							task_gen = None
							try:
								try: task_gen = task._sched_gen
								except AttributeError: task_gen = task._sched_gen = task(self._context)
								in_tasks = task_gen.next()
							except StopIteration:
								if __debug__ and is_debug: debug('sched: thread: ' + str(i) + ': task processed: ' + str(task) + ' ' + str(task.out_tasks))
								task._sched_processed = True
							except:
								if task_gen is not None:
									try: task_gen.close() # or del task_gen. note: no close() on python 2.4
									except: pass # we only want the original exception
								raise
							else:
								task._sched_stacked = False
								notify = 0
								task._sched_in_task_todo_count += len(in_tasks)
								for in_task in in_tasks:
									in_task._sched_out_tasks.append(task)
									if not in_task._sched_stacked and in_task._sched_in_task_todo_count == 0:
										if __debug__ and is_debug: debug('sched: thread: ' + str(i) + ': in task stacked: ' + str(in_task))
										self._task_stack.append(in_task)
										in_task._sched_stacked = True
									 	notify += 1
								self._todo_count += notify
								if notify > 1: self._condition.notify(notify - 1)
								continue
						task._sched_stacked = False
						self._todo_count -= 1
						notify = -1
						for out_task in task._sched_out_tasks:
							out_task._sched_in_task_todo_count -= 1
							if not out_task._sched_stacked and out_task._sched_in_task_todo_count == 0:
								if __debug__ and is_debug: debug('sched: thread: ' + str(i) + ': out task stacked: ' + str(out_task))
								self._task_stack.append(out_task)
								out_task._sched_stacked = True
								notify += 1
						task._sched_out_tasks = []
						if notify > 0: self._condition.notify(notify)
						elif notify < 0 and self._done_condition():
							self._condition.notifyAll()
							break
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

	def _parallel_wait(self, *tasks):
		if __debug__ and is_debug:
			debug('sched: task stack: ' + str([str(t) for t in self._task_stack]))
			debug('sched: parallel_wait: ' + str([str(t) for t in tasks]))
		count = len(tasks)
		if count == 0: return
		if count != 1: self._parallel_no_wait(*tasks[1:])
		if tasks[0]._sched_stacked: yield self._wait(*tasks)
		else:
			self._todo_count += 1
			tasks[0]._sched_stacked = True
			self._process_one_task(tasks[0])
			if count != 1: yield self._wait(*tasks[1:])
		if __debug__ and is_debug:
			for task in tasks: assert task._sched_processed, task
	
	def _parallel_no_wait(self, *tasks):
		if __debug__ and is_debug:
			debug('sched: task stack: ' + str([str(t) for t in self._task_stack]))
			debug('sched: parallel_no_wait: ' + str([str(t) for t in tasks]))
		notify = 0
		for task in reversed(tasks):
			if not task._sched_processed and not task._sched_stacked:
				self._task_stack.append(task)
				task._sched_stacked = True
				notify += 1
		if notify != 0:
			self._todo_count += notify
			self._condition.notify(notify)

	def _wait(self, *tasks):
		for task in tasks:
			if __debug__ and is_debug: assert task._sched_stacked, task
			while True:
				if __debug__ and is_debug:
					debug('sched: task stack: ' + str([str(t) for t in self._task_stack]))
					debug('sched: waiting for tasks: ' + str([str(t) for t in tasks if not t._sched_processed]))
				while not task._sched_processed and not self._stop_requested and len(self._task_stack) == 0: self._condition.wait(timeout = self.timeout)
				if self._stop_requested: raise StopIteration
				if task._sched_processed: break
				yield ()
			if __debug__ and is_debug: assert task._sched_processed, task
