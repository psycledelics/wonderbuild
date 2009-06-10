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
			self._scheduler = scheduler
			self.parallel_wait = scheduler._parallel_wait
			self.parallel_no_wait = scheduler._parallel_no_wait

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
			if __debug__ and is_debug: debug('sched: stack: push: todo: ' + str(self._todo_count) + ', stack length: ' + str(len(self._task_stack)) + ', task: ' + str(task))

		if self.thread_count == 1:
			self._lock = Scheduler._DummyLock()
			self._cond = Scheduler._DummyCondition()
		else:
			self._lock = threading.Lock()
			self._cond = threading.Condition(self._lock)
		self._context = Scheduler.Context(self)

		self._stop_requested = False

		if self.thread_count != 1:
			if __debug__ and is_debug: debug('sched: starting threads: ' + str(self.thread_count))
			#sys.setcheckinterval(interval)
			self._joining = False
			self._threads = []
			remaining_start_count = self.thread_count - 1
			remaining_start_cond = threading.Condition(threading.Lock())
			remaining_start_cond.acquire()
			try:
				thread_id = 1
				t = threading.Thread(
					target = self._thread_loop,
					args = (thread_id, remaining_start_count - 1, remaining_start_cond),
					name = 'scheduler-thread-' + str(thread_id)
				)
				t.setDaemon(True)
				t.start()
				self._threads.append(t)
				while len(self._threads) != remaining_start_count: remaining_start_cond.wait(timeout = self.timeout)
			finally: remaining_start_cond.release()

		self._joining = True
		try: self._thread_loop(0, 0, None) # note: no timeout handling here
		finally:
			if self.thread_count != 1:
				if __debug__ and is_debug: debug('sched: joining threads')
				self._cond.acquire()
				try:
					self._joining = True
					self._cond.notifyAll()
				finally: self._cond.release()
				for t in self._threads: t.join(timeout = self.timeout)
			if hasattr(self, 'exception'):
				for task in self._task_stack: self._close_gen(task)
				if isinstance(self.exception, UserReadableException): raise self.exception
				else: raise UserReadableException, 'An exception occurred, see stack trace above.'
	
	def _close_gen(self, task):
		try:
			try: task_gen = task._sched_gen
			except AttributeError: pass
			else:
				if task_gen is not None: task_gen.close()
				task._sched_gen = None
		finally:
			out_tasks = task._sched_out_tasks
			task._out_tasks = None
			for out_task in out_tasks: self._close_gen(out_task)

	def _thread_loop(self, thread_id, remaining_start_count, remaining_start_cond):
		if __debug__ and is_debug: debug('sched: thread: ' + str(thread_id) + ': started')
		if remaining_start_cond is not None:
			remaining_start_cond.acquire()
			try:
				if remaining_start_count == 0: remaining_start_cond.notify()
				else:
					t = threading.Thread(
						target = self._thread_loop,
						args = (thread_id + 1, remaining_start_count - 1, remaining_start_cond),
						name = 'scheduler-thread-' + str(thread_id + 1)
					)
					t.setDaemon(True)
					t.start()
					self._threads.append(t)
			finally: remaining_start_cond.release()
		self._cond.acquire()
		try:
			while True:
					while not self._done_or_break_cond() and len(self._task_stack) == 0:
						if __debug__ and is_debug: debug('sched: thread: ' + str(thread_id) + ': waiting, todo: ' + str(self._todo_count) + ', stack: ' + str([str(t) for t in self._task_stack]))
						self._cond.wait(timeout = self.timeout)
						if __debug__ and is_debug: debug('sched: thread: ' + str(thread_id) + ': notified')
					if __debug__ and is_debug: debug('sched: thread: ' + str(thread_id) + ': condition met: stop_requested: ' + str(self._stop_requested) + ', todo: ' + str(self._todo_count) + ', stack: ' + str([str(t) for t in self._task_stack]))
					if self._done_or_break_cond(): break
					task = self._task_stack.pop()
					if __debug__ and is_debug: debug('sched: thread: ' + str(thread_id) + ': stack pop: task: ' + str(task) + ', out tasks: ' + str(task._sched_out_tasks))
					if not task._sched_processed:
						if __debug__ and is_debug: debug('sched: thread: ' + str(thread_id) + ': task not yet processed: ' + str(task))
						self._context._thread_id = thread_id
						task_gen = None
						try:
							try: task_gen = task._sched_gen
							except AttributeError: task_gen = task._sched_gen = task(self._context)
							in_tasks = task_gen.next()
						except StopIteration:
							if __debug__ and is_debug: debug('sched: thread: ' + str(thread_id) + ': task processed: ' + str(task) + ', out tasks: ' + str([str(t) for t in task._sched_out_tasks]))
							task._sched_processed = True
						except:
							if task_gen is not None: self._close_gen(task)
							raise
						else:
							if __debug__ and is_debug: debug('sched: thread: ' + str(thread_id) + ': task: ' + str(task) + ', in tasks: ' + str([str(t) for t in in_tasks]))
							task._sched_stacked = False
							notify = 0
							task._sched_in_task_todo_count += len(in_tasks)
							for in_task in in_tasks:
								in_task._sched_out_tasks.append(task)
								if not in_task._sched_stacked and in_task._sched_in_task_todo_count == 0:
									if __debug__ and is_debug: debug('sched: thread: ' + str(thread_id) + ': task: ' + str(task) + ', in task pushed on stack: ' + str(in_task))
									self._task_stack.append(in_task)
									in_task._sched_stacked = True
								 	notify += 1
							self._todo_count += notify
							if notify > 1: self._cond.notify(notify - 1)
							continue
					task._sched_stacked = False
					self._todo_count -= 1
					notify = -1
					for out_task in task._sched_out_tasks:
						out_task._sched_in_task_todo_count -= 1
						if not out_task._sched_stacked and out_task._sched_in_task_todo_count == 0:
							if __debug__ and is_debug: debug('sched: thread: ' + str(thread_id) + ': task:' + str(task) + ', out task pushed on stack: ' + str(out_task))
							self._task_stack.append(out_task)
							out_task._sched_stacked = True
							notify += 1
					task._sched_out_tasks = []
					if notify > 0: self._cond.notify(notify)
					elif notify < 0 and self._done_cond():
						self._cond.notifyAll()
						break
		except Exception, e:
			self.exception = e
			self._stop_requested = True
			self._cond.notifyAll()
			if not isinstance(e, UserReadableException):
				import traceback
				traceback.print_exc()
		finally:
			if __debug__ and is_debug: debug('sched: thread: ' + str(thread_id) + ': terminated')
			self._cond.release()

	def _done_cond(self): return self._joining and self._todo_count == 0
	
	def _done_or_break_cond(self): return self._done_cond() or self._stop_requested

	def _parallel_wait(self, *tasks):
		if __debug__ and is_debug: debug('sched: parallel_wait: ' + str([str(t) for t in tasks]))
		tasks_to_yield = tuple(t for t in tasks if not t._sched_processed)
		if len(tasks_to_yield) != 0:
			if __debug__ and is_debug: debug('sched: yield tasks: ' + str([str(t) for t in tasks_to_yield]))
			#XXX
			sched_ctx = yield tasks_to_yield
		if __debug__ and is_debug:
			debug('sched: thread: parallel_wait done: ' + str([str(t) for t in tasks]))
			for t in tasks: assert t._sched_processed, t
	
	def _parallel_no_wait(self, *tasks):
		if __debug__ and is_debug: debug('sched: thread: parallel_no_wait: ' + str([str(t) for t in tasks]))
		notify = 0
		for t in reversed(tasks):
			if not t._sched_processed and not t._sched_stacked and t._sched_in_task_todo_count == 0:
				if __debug__ and is_debug: debug('sched: thread: task pushed on stack: ' + str(t))
				self._task_stack.append(t)
				t._sched_stacked = True
				notify += 1
		if notify != 0:
			self._todo_count += notify
			self._cond.notify(notify)
