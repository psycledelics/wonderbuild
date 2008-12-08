#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import sys, os, gc, cPickle

from scheduler import Scheduler
from filesystem import FileSystem
from logger import is_debug, debug
from cpp_include_scanner import IncludeScanner

class Project(object):
	def __init__(self, bld_path = '++wonderbuild'):
		gc.disable()
		try:
			try: f = file(os.path.join(bld_path, 'state-and-cache'), 'rb')
			except IOError: raise
			else:
				try: self.state_and_cache = cPickle.load(f)
				except Exception, e:
					print >> sys.stderr, 'could not load pickle:', e
					raise
				finally: f.close()
		except: self.state_and_cache = {}
		finally: gc.enable()

		self.confs = []
		self.tasks = []
		self.aliases = {} # {name: [tasks]}

		try: self.task_sigs = self.state_and_cache[self.__class__.__name__]
		except KeyError:
			if  __debug__ and is_debug: debug('project: all anew')
			self.task_sigs = {} # {task.uid: task.sig}
			self.state_and_cache[self.__class__.__name__] = self.task_sigs

		self.fs = FileSystem(self.state_and_cache)
		self.src_node = self.fs.cur
		self.bld_node = self.fs.cur.rel_node(bld_path)
		
	def add_task(self, task, aliases):
		self.tasks.append(task)
		if aliases is not None:
			if __debug__ and is_debug: debug('project: aliases: ' + str(aliases) + ' ' + str(task))
			for a in aliases:
				try: self.aliases[a].append(task)
				except KeyError: self.aliases[a] = [task]

	def conf(self):
		self.cpp = IncludeScanner(self.fs, self.state_and_cache)
		for c in self.confs: c.conf()
		
	def help(self):
		for c in self.confs: c.help()

	def build(self, tasks):
		s = Scheduler()
		s.start()
		for t in tasks: s.add_task(t)
		s.join()

	def dump(self):
		gc.disable()
		try:
			self.bld_node.make_dir()
			f = file(os.path.join(self.bld_node.path, 'state-and-cache'), 'wb')
			try: cPickle.dump(self.state_and_cache, f, cPickle.HIGHEST_PROTOCOL)
			finally: f.close()
		finally: gc.enable()
