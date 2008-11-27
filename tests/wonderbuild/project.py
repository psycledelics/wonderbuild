#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from scheduler import Scheduler
from filesystem import FileSystem
from options import options
from logger import debug

class Project(object):
	def __init__(self):
		self.aliases = {}
		self.tasks = {}
		self.task_sigs = {}
		self.build_dir = '++build'
		self.cache_path = os.path.join(self.build_dir, 'wonderbuild-cache')
		self.fs = FileSystem(os.path.join(self.cache_path, 'filesystem'))
		
	def add_aliases(self, task, aliases)
		self.tasks.append(task)
		if aliases is not None:
			debug('project: ' + str(aliases))
			for a in aliases:
				try: self.aliases[a].append(task)
				except KeyError: self.aliases[a] = [task]

	def build(self, tasks):
		s = Scheduler()
		s.start()
		for t in tasks: s.add_task(t)
		s.join()

