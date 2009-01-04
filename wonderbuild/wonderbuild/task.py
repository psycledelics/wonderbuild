#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import sys, os, subprocess

from logger import out, is_debug, debug, colored

class Task(object):
	def __init__(self, project, aliases = None):
		self.project = project
		project.add_task(self, aliases)
		self.in_tasks = []
		self.out_tasks = []
		self.dyn_in_tasks_called = False
		self.in_tasks_visited = 0
		self.processed = False

	def add_in_task(self, task):
		self.in_tasks.append(task)
		task.out_tasks.append(self)

	def add_out_task(self, task):
		self.out_tasks.append(task)
		task.in_tasks.append(self)

	def dyn_in_tasks(self, sched_context): return None

	def need_process(self):
		# This default implementation is not really useful
		if len(self.in_tasks) == 0: return True
		for in_task in self.in_tasks:
			if in_task.processed: return True
		return False

	def process(self): self.processed = True

	def print_desc(self, desc, color = '7;1'):
		out.write(colored(color, 'wonderbuild: task: ' + desc) + '\n')
		out.flush()

def exec_subprocess(args, env = None, cwd = None):
	if __debug__ and is_debug: debug('exec: ' + str(cwd) + ' ' + str(env) + ' ' + str(args))
	return subprocess.call(
		args = args,
		bufsize = -1,
		stdout = None,
		stderr = None,
		env = env,
		cwd = cwd
	)

def exec_subprocess_pipe(args, env = None, cwd = None, silent = False):
	if __debug__ and is_debug: debug('exec: pipe: ' + str(cwd) + ' ' + str(env) + ' ' + str(args))
	p = subprocess.Popen(
		args = args,
		bufsize = -1,
		stdout = subprocess.PIPE,
		stderr = subprocess.PIPE,
		env = env,
		cwd = cwd
	)
	out, err = p.communicate()
	if not silent:
		if len(out): sys.stdout.write(out)
		if len(err):
			s = ''
			for line in err.split('\n')[:-1]: s += colored('7;1;31', 'error:') + ' ' + line + '\n'
			sys.stderr.write(s)
	elif __debug__ and is_debug:
		if len(out):
			for line in out.split('\n')[:-1]: debug('exec: pipe: ' + colored('7;1;32', 'out') + ': ' + line)
		if len(err):
			s = ''
			for line in err.split('\n')[:-1]: debug('exec: pipe: ' + colored('7;1;31', 'err') + ': ' + line)
			debug(s)
	return p.returncode, out, err
