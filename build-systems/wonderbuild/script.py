#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2009-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from task import ProjectTask

default_script_file = 'wonderbuild_script.py'

class ScriptLoaderTask(ProjectTask):
	@staticmethod
	def shared(project, script):
		try: script_tasks = project.script_tasks
		except AttributeError: script_tasks = project.script_tasks = {}
		else:
			try: script_task = script_tasks[script]
			except KeyError: pass
			else: return script_task
		script_task = script_tasks[script] = ScriptLoaderTask(project, script)
		return script_task

	def __init__(self, project, script):
		ProjectTask.__init__(self, project)
		self.script = script
		
	def __str__(self): return 'script ' + str(self.script) + ' (loading)'

	def __call__(self, sched_ctx):
		script = self.script
		if script.is_dir: script = script / default_script_file
		d = {}
		execfile(script.path, d)
		self.task = d['Wonderbuild'](self.project, script.parent)
		sched_ctx.parallel_wait(self.task)

class ScriptTask(ProjectTask):
	@staticmethod	
	def shared(project, *scripts):
		script_tasks = [ScriptLoaderTask.shared(project, script) for script in scripts]
		project.sched_ctx.parallel_wait(*script_tasks)
		if len(scripts) == 1: return script_tasks[0].task
		else: return (script_task.task for script_task in script_tasks)

	def __init__(self, project, src_dir):
		ProjectTask.__init__(self, project)
		self.src_dir = src_dir

	def __str__(self): return 'script ' + str(self.src_dir) + ' (execution)'
