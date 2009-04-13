#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

default_script_file = 'wonderbuild_script.py'

class Script(object):
	def __init__(self, project, script):
		self.project = project
		if script.is_dir: script = script / default_script_file
		self.script = script
	
	def __call__(self):
		d = {}
		execfile(self.script.path, d)
		tasks = d['wonderbuild_script'](self.project, self.script.parent)
		return tasks
