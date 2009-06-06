#! /usr/bin/env python

class Task:
	def __init__(self, i):
		self.processed = self.queued = False
		self.in_task_todo_count = 0
		self.out_tasks = []
		self.i = i
		
	def __call__(self, i):
		lock.release()
		try:
			out(i, 'begin', self.i)
			z = 0
			for x in xrange(1000000): z += x
			out(i, 'end', self.i)
		finally: lock.acquire()
		raise StopIteration

class Task0(Task):
	def __call__(self, i):
		for x in sched(i, t1, t2): i = yield x
		Task.__call__(self, i)
t0 = Task0(0)

t1 = Task(1)

t2 = Task(2)

class Task3(Task):
	def __call__(self, i):
		for x in sched(i, t0): i = yield x
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
	
def xxxsched(i, *tasks):
	out(i, 'sched', [t.i for t in tasks])
	global todo
	count = len(tasks)
	if count == 0: return
	if count != 1:
		notify = 0
		for task in reversed(tasks[1:]):
			if not task.processed and not task.queued:
				out(i, 'task queued', task.i)
				queue.append(task)
				task.queued = True
				notify += 1
		if notify != 0:
			todo += notify
			cond.notify(notify)
	if tasks[0].queued:
		for x in wait(i, *tasks): i = yield x
	else:
		if not tasks[0].processed: i = yield (tasks[0],)
		if count != 1:
			for x in wait(i, *tasks[1:]): i = yield x
	for task in tasks: assert task.processed, task

def wait(i, *tasks):
	global todo
	for task in tasks:
		while True:
			out(i, 'wait for', task.i)
			while not task.processed and len(queue) == 0:
				out(i, 'wait for', task.i)
				cond.wait()
			if task.processed: break
			i = yield ()
		assert task.processed, task

def sched(i, *tasks):
	out(i, 'sched', [t.i for t in tasks])
	i = yield tasks

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
			task = queue.pop()
			if not task.processed:
				out(i, 'process', task.i)
				task_gen = None
				try:
					try: task_gen = task._gen
					except AttributeError:
						task_gen = task._gen = task(i)
						in_tasks = task_gen.next()
					else: in_tasks = task_gen.send(i)
				except StopIteration:
					out(i, 'processed', task.i, 'out tasks', [t.i for t in task.out_tasks])
					task.processed = True
				except:
					if task_gen is not None: task_gen.close()
					raise
				else:
					out(i, 'task', task.i, 'in tasks', [t.i for t in in_tasks])
					task.queued = False
					notify = 0
					task.in_task_todo_count += len(in_tasks)
					for in_task in in_tasks:
						in_task.out_tasks.append(task)
						if not in_task.queued and in_task.in_task_todo_count == 0:
							out(i, 'task', task.i, 'in task queued', in_task.i)
							queue.append(in_task)
							in_task.queued = True
						 	notify += 1
					todo += notify
					if notify > 1: cond.notify(notify - 1)
					continue
			task.queued = False
			todo -= 1
			notify = -1
			for out_task in task.out_tasks:
				out_task.in_task_todo_count -= 1
				if not out_task.queued and out_task.in_task_todo_count == 0:
					out(i, 'task', task.i, 'out task queued', out_task.i)
					queue.append(out_task)
					out_task.queued = True
					notify += 1
			task.out_tasks = []
			if notify > 0: cond.notify(notify)
			elif notify < 0 and todo == 0:
				cond.notifyAll()
				break
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
