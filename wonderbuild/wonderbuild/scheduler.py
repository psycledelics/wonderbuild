#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2007-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os, threading
#from collections import deque
#python 2.5.0a1 from __future__ import with_statement

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
		self._todo_count = self._task_count = 0

	class Context(object):
		def __init__(self, scheduler):
			self.thread_count = scheduler.thread_count
			self.lock = scheduler._lock

	def process(self, tasks):
		if self.thread_count == 1:
			self._pre_start()
			for t in tasks: self.add_task(t)
			self._joining = True
			self._thread_function(0) # XXX need a way to handle timeout
			self._post_join()
		else:
			self.start()
			for t in tasks: self.add_task(t)
			self.join()
		
	def _pre_start(self):
		self._tasks = set()
		self._task_queue = []#deque()
		self._todo_count = self._task_count
		self._running_count = 0
		self._stop_requested = self._joining = False
		self._lock = threading.Lock()
		self._condition = threading.Condition(self._lock)
		self._context = Scheduler.Context(self)

	def start(self):
		if __debug__ and is_debug: debug('sched: starting threads: ' + str(self.thread_count))
		self._pre_start()
		self._threads = []
		for i in xrange(self.thread_count):
			t = threading.Thread(target = self._thread_function, args = (i,), name = 'scheduler-thread-' + str(i))
			#t.daemon = True
			t.setDaemon(True)
			t.start()
			self._threads.append(t)

	def add_task(self, task):
		self._condition.acquire()
		try:
			if task in self._tasks: return
			self._tasks.add(task)
			self._todo_count += 1
			self._task_count += 1
			if len(task.in_tasks) == 0:
				self._task_queue.append(task)
				self._condition.notify()
			else:
				self._condition.release()
				try:
					for t in task.in_tasks: self.add_task(t)
				finally: self._condition.acquire()
			if __debug__ and is_debug: debug('sched: add task ' + str(self._todo_count) + ' ' + str(task.__class__))
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
		del self._tasks
		if hasattr(self, 'exception'): raise self.exception
	
	def _thread_function(self, i):
		if __debug__ and is_debug: debug('sched: thread: ' + str(i) + ': started')
		self._condition.acquire()
		try:
			try:
				while True:
					while (not self._joining or self._todo_count != 0) and not self._stop_requested and len(self._task_queue) == 0:
						if __debug__ and is_debug: debug('sched: thread: ' + str(i) + ': waiting')
						self._condition.wait(timeout = self.timeout)
						if __debug__ and is_debug: debug('sched: thread: ' + str(i) + ': notified ' + str(self._joining) + ' ' + str(self._todo_count) + '-' + str(self._running_count) + '/' + str(self._task_count) + ' ' + str(self._stop_requested))
					if self._joining and self._todo_count == 0 or self._stop_requested: break
					task = self._task_queue.pop()
					if not task.dyn_in_tasks_called:
						dyn_in_tasks = task.dyn_in_tasks(self._context)
						task.dyn_in_tasks_called = True
						if dyn_in_tasks is not None and len(dyn_in_tasks) != 0:
							self._task_queue += dyn_in_tasks
							notify = len(dyn_in_tasks)
							self._todo_count += notify
							if notify > 1: self._condition.notify(notify - 1)
							continue
					if task.need_process():
						self._condition.release()
						try: task.process()
						finally: self._condition.acquire()
					self._todo_count -= 1
					if self._todo_count == 0 and self._joining:
						self._condition.notifyAll()
						break
					notify = -1
					for out_task in task.out_tasks:
						out_task.in_tasks_visited += 1
						if out_task.in_tasks_visited == len(out_task.in_tasks):
							self._task_queue.append(out_task)
							notify += 1
					if notify > 0: self._condition.notify(notify)
			except Exception, e:
				self.exception = e
				self._stop_requested = True
				self._condition.notifyAll()
				raise
		finally:
			if __debug__ and is_debug: debug('sched: thread: ' + str(i) + ': terminated')
			self._condition.release()
