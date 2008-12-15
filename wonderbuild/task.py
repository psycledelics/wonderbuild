#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import sys, os, subprocess

from logger import out, is_debug, debug, colored

class Schedulable(object):
	def __init__(self):
		self.in_tasks = []
		self.out_tasks = []
		self.dyn_in_tasks_called = False
		self.processed = False
		self.executed = False

	def dyn_in_tasks(self): return None

	def need_process(self): raise Exception, str(self.__class__) + ' must implement the need_process method'

	def process(self): pass
	
	def update_sig(self): raise Exception, str(self.__class__) + ' must implement the update_sig method'

class Task(Schedulable):
	def __init__(self, project, aliases = None):
		Schedulable.__init__(self)
		#self.in_nodes = []
		#self.out_nodes = []
		self.project = project
		project.add_task(self, aliases)

	def add_in_task(self, task):
		self.in_tasks.append(task)
		task.out_tasks.append(self)

	def add_out_task(self, task):
		self.out_tasks.append(task)
		task.in_tasks.append(self)

	@property
	def uid(self): raise Exception, str(self.__class__) + ' must implement the uid property'
	
	@property
	def old_sig(self):
		try: return self.project.task_states[self.uid]
		except KeyError: return None
	
	@property
	def sig(self): raise Exception, str(self.__class__) + ' must implement the sig property'

	def need_process(self): return self.sig != self.old_sig

	def update_sig(self): self.project.task_states[self.uid] = self.sig

	def print_desc(self, desc, color = '7;1'):
		out.write(colored(color, 'wonderbuild: task: ' + desc) + '\n')
		out.flush()

def exec_subprocess(args, env = None, out_stream = sys.stdout, err_stream = sys.stderr, silent = False):
	if __debug__ and is_debug: debug('exec: ' + str(args))
	p = subprocess.Popen(
		args = args,
		stdout = subprocess.PIPE,
		stderr = subprocess.PIPE,
		env = env
	)
	out, err = p.communicate()
	if not silent:
		out_stream.write(out)
		if len(err):
			s = ''
			for line in err.split('\n')[:-1]: s += colored('7;1;31', 'error:') + ' ' + line + '\n'
			err_stream.write(s)
	return p.returncode, out, err
