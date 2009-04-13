#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2009-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from task import Task

default_script_file = 'wonderbuild_script.py'

class ProjectScriptTask(Task):
	def __init__(self, project, script):
		Task.__init__(self, project)
		if script.is_dir: script = script / default_script_file
		self.script = script
		
	def __str__(self): return str(self.script)

	def __call__(self, sched_context):
		d = {}
		execfile(self.script.path, d)
		self.task = d['Wonderbuild'](self.project, self.script.parent)
		sched_context.parallel_wait(self.task)

class ScriptTask(Task):
	def __init__(self, project, src_dir):
		Task.__init__(self, project)
		self.src_dir = src_dir

	def __str__(self): return str(self.__class__) + ' in src dir ' + str(self.src_dir)
