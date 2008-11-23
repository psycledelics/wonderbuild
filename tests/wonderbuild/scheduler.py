#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2007-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import threading
#python 2.5.0a1 from __future__ import with_statement

class Scheduler():
	def __init__(self):
		self.nodes = []
		self.thread_count = 1
		self.timeout = 3600.0

	def start(self):
		self._nodes_queue = []
		for n in self.nodes:
			if not n.in_nodes(): self._nodes_queue.append(n)
		self._condition = threading.Condition(threading.Lock())
		self._stop_requested = False
		self._threads = []
		for i in xrange(self.thread_count):
			t = threading.Thread(target = _thread_function, args = (self,), name = 'scheduler-thread-' + str(i))
			t.setDaemon(True)
			t.start()
			self._threads.append(t)
	
	def stop(self):
		self._condition.acquire()
		try: self._stop_requested = True
		finally: self._condition.release()
		self._condition.notifyAll()
		for t in self._threads: t.join(timeout = self.timeout)
		del self._threads
		del self._condition
		del self._nodes_queue
	
	def _thread_function(self):
		while True:
			self._condition.acquire()
			try:
				while not self._stop_requested and not self._nodes_queue: self._condition.wait(timeout = self._timeout)
				if self._stop_requested: return
				node = self._nodes_queue.pop()
			finally: self._condition.release()

			dyn_prec = node.dyn_prec()
			if dyn_prec is not None:
				self._condition.acquire()
				try: self._nodes_queue += dyn_prec
				finally: self._condition.release()
				notify = len(dyn_prec)
				if notify > 2: self._condition.notifyAll()
				elif notify > 1: self._condition.notify()
			else:
				node.process()
				notify = 0
				self._condition.acquire()
				try:
					for out_node in node.out_nodes():
						ready = True
						for node in out_node.iter_in_nodes():
							if not node.processed():
								ready = False
								break
						if ready:
							self._nodes_queue.append(out_node)
							++notify
				finally: self._condition.release()
				if notify > 2: self._condition.notifyAll()
				elif notify > 1: self._condition.notify()
