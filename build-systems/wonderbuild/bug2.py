#! /usr/bin/env python

class Task:
	def __init__(self, i):
		self.processed = False
		self.queued = False
		self.i = i
		
	def __call__(self, i):
		lock.release()
		try:
			out(i, 'begin', self.i)
			z = 0
			for x in xrange(1000000): z += x
			out(i, 'end', self.i)
		finally: lock.acquire()

class Task0(Task):
	def __call__(self, i):
		sched(i, t1, t2)
		Task.__call__(self, i)
t0 = Task0(0)

t1 = Task(1)

t2 = Task(2)

class Task3(Task):
	def __call__(self, i):
		sched(i, t0)
		Task.__call__(self, i)
t3 = Task3(3)

queue = [t3, t0]
for task in queue: task.queued = True
todo = len(queue)

import threading
lock = threading.Lock()
cond = threading.Condition(lock)

import sys
def out(*args):
	out = sys.stdout
	out.write(' '.join((str(a) for a in args)) + '\n')
	#out.flush()
	
def sched(i, *tasks):
	global todo
	count = len(tasks)
	if count > 1:
		notify = 0
		for task in tasks[1:]:
			if not task.processed and not task.queued:
				task.queued = True
				queue.append(task)
				notify += 1
		if notify != 0:
			todo += notify
			cond.notify(notify)
	task = tasks[0]
	if not task.processed:
		if task.queued: wait(i, *tasks)
		else:
			todo += 1
			task.queued = True
			do(i, task)
	if count > 1: wait(i, *tasks[1:])

def do(i, x):
	global todo
	if not isinstance(x, Task):
		cr = x
		try: cr.send(i)
		except StopIteration: 
			todo -= 1
			cond.notifyAll()
		else: queue.append(cr)
	else:
		task = x
		out(i, 'do', task.i)
		task(i)
		task.processed = True
		todo -= 1
		cond.notifyAll()

def wait(i, *tasks):
	global todo
	for task in tasks:
		while True:
			out(i, 'wait for', task.i)
			while not task.processed and len(queue) == 0:
				out(i, 'wait for', task.i)
				cond.wait()
			if task.processed: break
			cr = coroutine(task)
			cr.next()
			if task.processed: break
			queue.append(cr)
			todo += 1
			do(i, queue.pop())

def coroutine(task):
	i = yield None
	while True:
		out(i, 'wait for', task.i, 'coroutine')
		while not task.processed:
			out(i, 'wait for', task.i, 'coroutine')
			cond.wait()
			if task.processed: break
			lock.release()
			try: i = yield None
			finally: lock.acquire()

def loop(i):
	global todo
	out(i, 'started')
	cond.acquire()
	try:
		while not joining: cond.wait()
		while True:
			while todo != 0 and len(queue) == 0:
				out(i, 'wait', 'todo', todo, [task.i for task in queue])
				cond.wait()
			if todo == 0: break
			do(i, queue.pop())
			if todo == 0: break
	finally: cond.release()
	out(i, 'terminated')

joining = False
cond.acquire()
try:
	threads = []
	for i in xrange(2):
		t = threading.Thread(target = loop, args = (i,), name = 'scheduler-thread-' + str(i))
		t.setDaemon(True)
		t.start()
		threads.append(t)
	joining = True
	cond.notifyAll()
finally: lock.release()
for t in threads: t.join()
