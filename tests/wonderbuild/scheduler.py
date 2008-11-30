#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2007-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import threading
#python 2.5.0a1 from __future__ import with_statement

class Scheduler():
	def __init__(self):
		self.thread_count = 2
		self.timeout = 3600.0
		self._task_count = 0
		self._todo_count = 0

	def start(self):
		self._task_queue = []
		self._todo_count = self._task_count
		self._running_count = 0
		self._stop_requested = False
		self._joining = False
		self._threads = []
		self._condition = threading.Condition(threading.Lock())
		for i in xrange(self.thread_count):
			t = threading.Thread(target = self._thread_function, args = (i,), name = 'scheduler-thread-' + str(i))
			t.setDaemon(True)
			t.start()
			self._threads.append(t)

	def add_task(self, task):
		if len(task.in_tasks) == 0:
			self._condition.acquire()
			try:
				self._task_count += 1
				self._todo_count += 1
				self._task_queue.append(task)
				self._condition.notify()
			finally: self._condition.release()
		else:
			self._condition.acquire()
			try:
				self._task_count += 1
				self._todo_count += 1
			finally: self._condition.release()
			for t in task.in_tasks: self.add_task(t)
		print 'add task', self._todo_count, '/', self._task_count, task

	def stop(self):
		self._condition.acquire()
		try:
			self._stop_requested = True
			self._condition.notifyAll()
		finally: self._condition.release()
		self.join()
		
	def join(self):
		self._condition.acquire()
		try:
			self._joining = True
			self._condition.notifyAll()
		finally: self._condition.release()
		for t in self._threads: t.join(timeout = self.timeout)
		del self._threads
		del self._condition
		del self._task_queue
	
	def _thread_function(self, i):
		print 'thread', i, 'running'
		while True:
			self._condition.acquire()
			try:
				while (not self._joining or self._todo_count != 0) and not self._stop_requested and len(self._task_queue) == 0:
					self._condition.wait(timeout = self.timeout)
				if self._joining and self._todo_count == 0 or self._stop_requested:
					print 'thread', i, 'return'
					return
				task = self._task_queue.pop()
				try:
					self._condition.release()
					try: dyn_in_tasks = task.dyn_in_tasks()
					finally: self._condition.acquire()
				except:
					self._stop_requested = True
					self._condition.notifyAll()
					raise
				if dyn_in_tasks is not None and len(dyn_in_tasks) != 0:
					self._task_queue += dyn_in_tasks
					notify = len(dyn_in_tasks)
					self._todo_count += notify
					self._task_count += notify
					if notify > 1: self._condition.notify(notify - 1)
				else:
					self._running_count += 1
					print 'thread', i, 'process', self._task_count - self._todo_count + self._running_count, '/', self._task_count, task
					try:
						self._condition.release()
						try: executed = task.process()
						finally: self._condition.acquire()
					except:
						self._stop_requested = True
						self._condition.notifyAll()
						raise
					self._running_count -= 1
					self._todo_count -= 1
					if executed: task.executed = True
					task.processed = True
					notify = 0
					for out_task in task.out_tasks:
						ready = True
						for task in out_task.in_tasks:
							if not task.processed:
								ready = False
								break
						if ready:
							self._task_queue.append(out_task)
							notify += 1
					if notify > 1: self._condition.notify(notify - 1)
			finally: self._condition.release()
