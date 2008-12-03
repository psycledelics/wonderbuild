#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import sys, os, gc, cPickle

from scheduler import Scheduler
from filesystem import FileSystem
from logger import is_debug, debug

class Project(object):
	def __init__(self, bld_path = '++wonderbuild'):
		self.aliases = {} # {name: [tasks]}
		self.tasks = []
		cache_path = 'cache'
		self.fs = FileSystem(os.path.join(bld_path, cache_path, 'filesystem'))
		self.src_node = self.fs.cur
		self.bld_node = self.fs.cur.rel_node(bld_path)
		self.cache_node = self.bld_node.rel_node(cache_path)
		self.load()
		
	def add_task(self, task, aliases):
		self.tasks.append(task)
		if aliases is not None:
			if __debug__ and is_debug: debug('project: aliases: ' + str(aliases) + ' ' + str(task))
			for a in aliases:
				try: self.aliases[a].append(task)
				except KeyError: self.aliases[a] = [task]

	def build(self, tasks):
		s = Scheduler()
		s.start()
		for t in tasks: s.add_task(t)
		s.join()

	def load(self):
		gc.disable()
		try:
			try: f = file(os.path.join(self.cache_node.abs_path, 'tasks'), 'rb')
			except IOError: raise
			else:
				try: self.task_sigs = cPickle.load(f)
				except Exception, e:
					print >> sys.stderr, 'could not load pickle:', e
					raise
				finally: f.close()
		except: self.task_sigs = {} # {task.uid: task.sig}
		finally: gc.enable()

	def dump(self):
		self.cache_node.make_dir()
		self.fs.dump()
		gc.disable()
		try:
			f = file(os.path.join(self.cache_node.path, 'tasks'), 'wb')
			try: cPickle.dump(self.task_sigs, f, cPickle.HIGHEST_PROTOCOL)
			finally: f.close()
		finally: gc.enable()
