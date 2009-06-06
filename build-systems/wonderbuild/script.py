#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2009-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from task import ProjectTask

default_script_file = 'wonderbuild_script.py'

class ScriptLoaderTask(ProjectTask):
	@staticmethod
	def shared(project, script):
		try: script_loader_tasks = project.script_loader_tasks
		except AttributeError: script_loader_tasks = project.script_loader_tasks = {}
		else:
			try: script_loader_task = script_loader_tasks[script]
			except KeyError: pass
			else: return script_loader_task
		script_loader_task = script_loader_tasks[script] = ScriptLoaderTask(project, script)
		return script_loader_task

	def __init__(self, project, script):
		ProjectTask.__init__(self, project)
		self.script = script
		
	def __str__(self): return 'script ' + str(self.script) + ' (loading)'

	def __call__(self, sched_ctx):
		script = self.script
		if script.is_dir: script = script / default_script_file
		d = {}
		execfile(script.path, d)
		self._script_task = d['Wonderbuild'](self.project, script.parent)
		for x in sched_ctx.parallel_wait(self._script_task): sched_ctx = yield x
	
	@property
	def script_task(self):
		try: return self._script_task
		except AttributeError: raise Exception, 'did you forget to process the ' + str(self) + ' task?'

class ScriptTask(ProjectTask):
	def __init__(self, project, src_dir):
		ProjectTask.__init__(self, project)
		self.src_dir = src_dir
		
	def __str__(self): return 'script ' + str(self.src_dir) + ' (execution)'
