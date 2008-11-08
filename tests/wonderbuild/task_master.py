#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

class TaskMaster:
	def __init__(self):
		self._tasks = []
		self._leaf_tasks = []
		self._queue = []

	def start(self):
		self._queue = self._leaf_tasks[:]
		self._stop_requested = False
		for t in self._threads: t.start()
	
	def stop(self):
		self._stop_requested = True
		for t in self._threads: t.join()
	
	def thread_function(self):
		while True:
			while not self._stop_requested and self._queue.empty: self._cond.wait()
			if self._stop_requested: return
			task = self._queue.pop
			self.process(task)
			self.lock()
			try:
				for o in task.out_nodes():
					for task in o.tasks():
						ready = True
						for i in task.in_nodes():
							for task in i.tasks():
								if not task.processed():
									ready = False
									break
						if ready:
							self._queue.push(task)
							self._cond.notify_all()
			finally:
				self.unlock()
	
	def process(self, task):
		task.process()
