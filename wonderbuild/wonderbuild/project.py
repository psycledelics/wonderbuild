#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import sys, os, gc, cPickle

from scheduler import Scheduler
from filesystem import FileSystem
from options import options, known_options, help
from logger import is_debug, debug

if __debug__ and is_debug: import time

known_options |= set(['--src-dir=', '--bld-dir='])
help['--src-dir='] = ('--src-dir=<dir>', 'use <dir> as the source dir', os.getcwd())
help['--bld-dir='] = ('--bld-dir=<dir>', 'use <dir> as the build dir', '<src-dir>' + os.sep + '++wonderbuild')

class Project(object):
	def __init__(self):
		src_path = bld_path = None
		for o in options:
			if o.startswith('--src-dir='): src_path = o[len('--src-dir='):]
			elif o.startswith('--bld-dir='): bld_path = o[len('--bld-dir='):]
		if src_path is None: src_path = help['--src-dir='][2]
		if bld_path is None: bld_path = os.path.join(src_path, '++wonderbuild')
		if src_path == bld_path: raise Exception, 'build dir and source dir are the same'
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
		self.cfgs = []
		self.task_aliases = {} # {name: [tasks]}
		self.fs = FileSystem(self.state_and_cache)
		self.src_node = self.fs.cur.node_path(src_path)
		self.bld_node = self.fs.cur.node_path(bld_path)
		self.processsing = False
		
	def options(self):
		for c in self.cfgs: c.options()

	def help(self):
		for c in self.cfgs: c.help()

	def configure(self):
		for c in self.cfgs: c.configure()

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
		self.processsing = True
		Scheduler().process(tasks)
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
