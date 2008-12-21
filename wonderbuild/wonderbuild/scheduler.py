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

known_options |= set(['--jobs', '--timeout', '--progress'])
help['--jobs'] = ('--jobs=<count>', 'use <count> threads in the scheduler to process the tasks', 'autodetected: ' + str(cpu_count))
help['--timeout'] = ('--timeout=<seconds>', 'wait at most <seconds> a task to complete before considering it\'s busted', '3600.0')
help['--progress'] = ('--progress', 'show output progress even when silent')

no_silent_progress = not silent or '--progress' in options

class Scheduler():
	def __init__(self):
		self.thread_count = 0
		self.timeout = 0
		for o in options:
			if o.startswith('--jobs='): self.thread_count = int(o[len('--jobs='):])
			elif o.startswith('--timeout='): self.timeout = float(o[len('--timeout='):])
		if self.thread_count == 0: self.thread_count = cpu_count
		if self.timeout == 0: self.timeout = 3600.0
		self._todo_count = self._task_count = 0

	def start(self):
		if __debug__ and is_debug: debug('sched: starting threads: ' + str(self.thread_count))
		self._tasks = set()
		self._task_queue = []#deque()
		self._todo_count = self._task_count
		self._running_count = 0
		self._stop_requested = False
		self._joining = False
		self._threads = []
		self._condition = threading.Condition(threading.Lock())
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
			self._task_count += 1
			self._todo_count += 1
			if len(task.in_tasks) == 0:
				self._task_queue.append(task)
				self._condition.notify()
			else:
				self._condition.release()
				try:
					for t in task.in_tasks: self.add_task(t)
				finally: self._condition.acquire()
			if __debug__ and is_debug: debug('sched: add task ' + str(self._todo_count) + '/' + str(self._task_count) + ' ' + str(task.__class__))
		finally: self._condition.release()

	def progress(self):
		max = self._task_count
		done = max - self._todo_count
		run = self._running_count
		pct = done == max and 100 or 100 * (done + run * .5) / max
		return '[' + str(int(pct)).rjust(3) + '%][' + str(done) + ' / ' + str(max) + ' done, ' + str(run) + ' running]'
	
	def stop(self):
		if __debug__:
			if is_debug: debug('sched: stopping threads')
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
		del self._condition
		del self._task_queue
		del self._tasks
		if hasattr(self, 'exception'): raise self.exception
	
	def _thread_function(self, i):
		if __debug__ and is_debug: debug('sched: thread: ' + str(i) + ': started')
		self._condition.acquire()
		try:
			while True:
				while (not self._joining or self._todo_count != 0) and not self._stop_requested and len(self._task_queue) == 0:
					if __debug__ and is_debug: debug('sched: thread: ' + str(i) + ': waiting')
					self._condition.wait(timeout = self.timeout)
					if __debug__ and is_debug: debug('sched: thread: ' + str(i) + ': notified ' + str(self._joining) + ' ' + str(self._todo_count) + '-' + str(self._running_count) + '/' + str(self._task_count) + ' ' + str(self._stop_requested))
				if self._joining and self._todo_count == 0 or self._stop_requested: break
				task = self._task_queue.pop()
				if not task.dyn_in_tasks_called:
					dyn_in_tasks = task.dyn_in_tasks()
					task.dyn_in_tasks_called = True
					if dyn_in_tasks is not None and len(dyn_in_tasks) != 0:
						self._task_queue += dyn_in_tasks
						notify = len(dyn_in_tasks)
						self._todo_count += notify
						self._task_count += notify
						if notify > 1: self._condition.notify(notify - 1)
						continue
				self._running_count += 1
				if __debug__ and is_debug: debug('sched: thread: ' + str(i) + ': process ' + self.progress() + ' ' + str(task))
				if len(task.in_tasks) == 0: execute = True
				else:
					execute = False
					for in_task in task.in_tasks:
						if in_task.executed:
							execute = True
							break
				if not execute:
					if __debug__ and is_debug: debug('sched: thread: ' + str(i) + ': skip task (in_tasks skipped) ' + str(task))
					task.executed = False
				elif not task.need_process():
					if __debug__ and is_debug: debug('sched: thread: ' + str(i) + ': skip task (same sig) ' + str(task))
					task.executed = False
				else:
					self._condition.release()
					try: task.process()
					finally: self._condition.acquire()
					task.update_sig()
					task.executed = True
				self._todo_count -= 1
				if no_silent_progress and task.executed: print colored('7;32', 'wonderbuild: progress: ' + self.progress())
				self._running_count -= 1
				if self._todo_count == 0 and self._joining:
					self._condition.notifyAll()
					break
				task.processed = True
				notify = -1
				for out_task in task.out_tasks:
					ready = True
					for task in out_task.in_tasks:
						if not task.processed:
							ready = False
							break
					if ready:
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
