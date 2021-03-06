#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2009-2010 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import sys, os, imp

from logger import is_debug, debug
from task import Task

default_script_file = 'wonderbuild_script.py'

def import_module(node):
	script_path = node.path
	modname = 'wonderbuild-script:' + script_path.replace(os.pardir, '_').replace('.', ',')
	try: return sys.modules[modname]
	except KeyError:
		if __debug__ and is_debug: debug('import: ' + script_path)
		path, name = os.path.split(script_path)
		name, ext  = os.path.splitext(name)
		path = [os.path.abspath(path)]
		file, script_path, data = imp.find_module(name, path)
		return imp.load_module(modname, file, script_path, data)

class ScriptLoaderTask(Task):
	@staticmethod
	def shared(project, script):
		try: return project.script_loader_tasks[script]
		except AttributeError: project.script_loader_tasks = {}
		except KeyError: pass
		script_loader_task = project.script_loader_tasks[script] = ScriptLoaderTask(project, script)
		return script_loader_task

	def __init__(self, project, script):
		Task.__init__(self)
		self.project = project
		self.script = script
		
	def __str__(self): return 'script ' + str(self.script) + ' (loading)'

	def __call__(self, sched_ctx):
		script = self.script
		if script.exists and script.is_dir: script = script / default_script_file
		self._script_task = import_module(script).Wonderbuild(self.project, script.parent)
		for x in sched_ctx.parallel_wait(self._script_task): yield x
	
	@property
	def script_task(self):
		try: return self._script_task
		except AttributeError: raise Exception, 'did you forget to process the ' + str(self) + ' task?'

class ScriptTask(Task):
	def __init__(self, project, src_dir):
		Task.__init__(self)
		self.project = project
		self.src_dir = src_dir
		self.default_tasks = []
		
	def __str__(self): return 'script ' + str(self.src_dir) + ' (execution)'
