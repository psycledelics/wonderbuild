#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os

from scheduler import Scheduler
from filesystem import FileSystem
from options import options
from logger import debug

class Project(object):
	def __init__(self):
		self.aliases = {} # {name: [tasks]}
		self.tasks = []
		self.task_sigs = {} # {task.uid: task.sig}
		self.build_dir = '++build'
		self.cache_dir = os.path.join(self.build_dir, 'wonderbuild-cache')
		self.fs = FileSystem(self)
		
	def add_aliases(self, task, aliases):
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

	def dump(self):
		if not os.path.exists(self.build_dir):
			os.mkdir(self.build_dir)
			os.mkdir(self.cache_dir)
		if not os.path.exists(self.cache_dir): os.mkdir(self.cache_dir)
		self.fs.dump()

