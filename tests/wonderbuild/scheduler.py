#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2007-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import threading
#python 2.5.0a1 from __future__ import with_statement

class Scheduler():
	def __init__(self):
		self.thread_count = 1
		self.timeout = 3600.0

	def start(self):
		self._task_queue = []
		self._condition = threading.Condition(threading.Lock())
		self._stop_requested = False
		self._threads = []
		for i in xrange(self.thread_count):
			t = threading.Thread(target = self._thread_function, name = 'scheduler-thread-' + str(i))
			t.setDaemon(True)
			t.start()
			self._threads.append(t)

	def add_task(self, task):
		if not task.in_tasks:
			self._condition.acquire()
			try:
				self._task_queue.append(task)
				self._condition.notify()
			finally: self._condition.release()
		else:
			for t in task.in_tasks: self.add_task(t)
	
	def stop(self):
		self._condition.acquire()
		try:
			self._stop_requested = True
			self._condition.notifyAll()
		finally: self._condition.release()
		for t in self._threads: t.join(timeout = self.timeout)
		del self._threads
		del self._condition
		del self._task_queue
		
	def join(self):
		x = 0
		for i in xrange(10000000): x += 1
		print x
		self.stop()
	
	def _thread_function(self):
		while True:
			self._condition.acquire()
			try:
				while not self._stop_requested and not self._task_queue: self._condition.wait(timeout = self.timeout)
				if self._stop_requested: return
				task = self._task_queue.pop()
			finally: self._condition.release()

			dyn_in_tasks = task.dyn_in_tasks()
			if dyn_in_tasks is not None:
				self._condition.acquire()
				try:
					self._task_queue += dyn_in_tasks
					notify = len(dyn_in_tasks)
					if notify > 2: self._condition.notifyAll()
					elif notify > 1: self._condition.notify()
				finally: self._condition.release()
			else:
				task.process()
				notify = 0
				self._condition.acquire()
				try:
					task.processed = True
					for out_task in task.out_tasks:
						ready = True
						for task in out_task.in_tasks:
							if not task.processed:
								ready = False
								break
						if ready:
							self._task_queue.append(out_task)
							++notify
					if notify > 2: self._condition.notifyAll()
					elif notify > 1: self._condition.notify()
				finally: self._condition.release()
