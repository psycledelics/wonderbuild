#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import sys, os, subprocess

from logger import is_debug, debug, colored

class Task(object):	
	def __init__(self, project, aliases = None):
		self.in_tasks = []
		self.out_tasks = []
		#self.in_nodes = []
		#self.out_nodes = []
		self.processed = False
		self.executed = False
		self.project = project
		project.add_task(self, aliases)

	def add_in_task(self, task):
		self.in_tasks.append(task)
		task.out_tasks.append(self)

	def add_out_task(self, task):
		self.out_tasks.append(task)
		task.in_tasks.append(self)

	def dyn_in_tasks(self): return None
		
	def process(self): pass
	
	@property
	def uid(self): return None
	
	@property
	def old_sig(self):
		try: return self.project.task_sigs[self.uid]
		except KeyError: return None
	
	@property
	def sig(self): return None
	
	def update_sig(self): self.project.task_sigs[self.uid] = self.sig
	
def exec_subprocess(args, desc = None, color = '7;1', env = None, out_stream = sys.stdout, err_stream = sys.stderr):
	if desc is None: desc = ' '.join(args)
	out_stream.write(colored(color, 'wonderbuild: task: ' + desc) + '\n')
	if __debug__ and is_debug: debug('task: exec: ' + str(args))
	p = subprocess.Popen(
		args = args,
		stdout = subprocess.PIPE,
		stderr = subprocess.PIPE,
		env = env
	)
	out, err = p.communicate()
	out_stream.write(out)
	if len(err):
		s = ''
		for line in err.split('\n')[:-1]: s += colored('7;1;31', 'error:') + ' ' + line + '\n'
		err_stream.write(s)
	return p.returncode, out, err
