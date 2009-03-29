#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import sys, os, gc, cPickle

from scheduler import Scheduler
from filesystem import FileSystem
from logger import is_debug, debug

if __debug__ and is_debug: import time

class Project(object):
	known_options = set(['src-dir', 'bld-dir', 'aliases', 'list-aliases'])

	#@staticmethod
	def help(self, help):
		help['src-dir'] = ('<dir>', 'use <dir> as the source dir', 'current working dir: ' + os.getcwd())
		help['bld-dir'] = ('<dir>', 'use <dir> as the build dir', '<src-dir>' + os.sep + '++wonderbuild')
		help['aliases'] = ('<name,...>', 'build tasks with aliases <name,...>, comma-separated list')
		help['list-aliases'] = (None, 'list the available task aliases')
		for o in self.option_handler_classes: o.help(help)

	def __init__(self, options):
		self.option_handler_classes = set() #([Project, Scheduler])
		self.options = options

		src_path = options.get('src-dir', None)
		if src_path is None: src_path = os.getcwd()
		
		bld_path = options.get('bld-dir', None)
		if bld_path is None: bld_path = os.path.join(src_path, '++wonderbuild')
		
		if src_path == bld_path: raise Exception, 'build dir and source dir are the same'

		self.list_aliases = 'list-aliases' in options

		self.task_aliases = {} # {name: [tasks]}
		aliases = options.get('aliases', None)
		if aliases is not None:
			if len(aliases): self.requested_task_aliases = aliases.split(',')
			else: self.requested_task_aliases = (None,)
		else: self.requested_task_aliases = None

		self.processsing = False

		gc_enabled = gc.isenabled()
		if gc_enabled: gc.disable()
		try:
			try:
				try: f = open(os.path.join(bld_path, 'state-and-cache'), 'rb')
				except IOError: raise
				else:
					try:
						try:
							if __debug__ and is_debug: t0 = time.time()
							self.state_and_cache = cPickle.load(f)
							if __debug__ and is_debug: debug('project: pickle: load time: ' + str(time.time() - t0) + ' s')
						except Exception, e:
							print >> sys.stderr, 'could not load pickle:', e
							raise
					finally: f.close()
			except: self.state_and_cache = {}
		finally:
			if gc_enabled: gc.enable()

		self.fs = FileSystem(self.state_and_cache)
		self.src_node = self.fs.cur.node_path(src_path)
		self.bld_node = self.fs.cur.node_path(bld_path)
		
	def add_task_aliases(self, task, aliases = None):
		if self.processsing: return # no need to add aliases during processing
		aliases = aliases is None and (None,) or (None,) + aliases
		if __debug__ and is_debug: debug('project: aliases: ' + str(aliases) + ' ' + str(task.__class__))
		for a in aliases:
			try: self.task_aliases[a].append(task)
			except KeyError: self.task_aliases[a] = [task]

	def tasks_with_aliases(self, task_aliases = None):
		tasks = set()
		if task_aliases is None: task_aliases = (None,)
		for a in task_aliases: tasks |= set(self.task_aliases[a])
		return tasks
		
	def process(self, tasks):
		if self.list_aliases:
			for k, v in self.task_aliases.iteritems():
				print k, [str(v) for v in v]
		else:
			if self.requested_task_aliases is not None: tasks = list(self.tasks_with_aliases(self.requested_task_aliases))
			self.processsing = True
			Scheduler(self.options).process(tasks)
			self.processsing = False

	def dump(self):
		#self.bld_node.forget()
		if False and __debug__ and is_debug: print self.state_and_cache
		gc_enabled = gc.isenabled()
		if gc_enabled: gc.disable()
		try:
			path = os.path.join(self.bld_node.path, 'state-and-cache')
			if __debug__ and is_debug: t0 = time.time()
			try: f = open(path, 'wb')
			except IOError:
				self.bld_node.make_dir()
				f = open(path, 'wb')
			try: cPickle.dump(self.state_and_cache, f, cPickle.HIGHEST_PROTOCOL)
			finally: f.close()
			if __debug__ and is_debug:
				debug('project: pickle: dump time: ' + str(time.time() - t0) + ' s')
				debug('project: pickle: file size: ' + str(int(os.path.getsize(path) * 1000. / (1 << 20)) * .001) + ' MiB')
		finally:
			if gc_enabled: gc.enable()
