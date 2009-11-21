#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import sys, os, gc, cPickle

from wonderbuild import abi_sig, UserReadableException
from task import Task, SharedTaskHolder
from script import ScriptLoaderTask
from filesystem import FileSystem
from logger import is_debug, debug, colored

if __debug__ and is_debug: import time

class Project(Task, SharedTaskHolder):

	known_options = set(['src-dir', 'bld-dir', 'tasks', 'list-tasks'])

	@staticmethod
	def generate_option_help(help):
		help['src-dir'] = ('<dir>', 'use <dir> as the source dir', 'current working dir: ' + os.getcwd())
		help['bld-dir'] = ('<dir>', 'use <dir> as the build dir', '<src-dir>' + os.sep + '++wonderbuild')
		help['tasks'] = ('<name,...>', 'build tasks with names <name,...>, comma-separated list', 'default')
		help['list-tasks'] = (None, 'list the available task names')

	def __init__(self, options, option_collector):
		Task.__init__(self)
		option_collector.option_decls.add(self.__class__)
	
		src_path = options.get('src-dir', None)
		if src_path is None: src_path = os.getcwd()
		
		bld_path = options.get('bld-dir', None)
		if bld_path is None: bld_path = os.path.join(src_path, '++wonderbuild')
		
		if src_path == bld_path: raise Exception, 'build dir and source dir are the same'

		self.list_aliases = 'list-tasks' in options

		self.task_aliases = {} # {name: [tasks]}
		aliases = options.get('tasks', None)
		if aliases is not None:
			if len(aliases): self.requested_task_aliases = aliases.split(',')
			else: self.requested_task_aliases = (None,)
		else: self.requested_task_aliases = None

		self.processsing = False

		gc_enabled = gc.isenabled()
		if gc_enabled:
			try: gc.disable()
			except NotImplementedError: pass # jython uses the gc of the jvm
		try: # python2.4 does not support try-except-finally
			try:
				try: f = open(os.path.join(bld_path, 'persistent.pickle'), 'rb')
				except IOError: raise
				else:
					try: # python2.4 does not support try-except-finally
						try:
							if __debug__ and is_debug: t0 = time.time()
							pickle_abi_sig = cPickle.load(f)
							if pickle_abi_sig != abi_sig:
								print >> sys.stderr, colored('33', 'wonderbuild: abi sig changed: discarding persistent pickle file, full rebuild will be performed')
								persistent = {}
							else: persistent = cPickle.load(f)
							if __debug__ and is_debug: debug('project: pickle: load time: ' + str(time.time() - t0) + ' s')
						except Exception, e:
							print >> sys.stderr, 'could not load pickle:', e
							raise
					finally: f.close()
			except: persistent = {}
		finally:
			if gc_enabled: gc.enable()

		self.fs = FileSystem(persistent, global_purge=aliases is None and not self.list_aliases)
		self.top_src_dir = self.fs.cur / src_path
		bld_dir = self.fs.cur / bld_path
		
		SharedTaskHolder.__init__(self, persistent, options, option_collector, bld_dir)

	def add_task_aliases(self, task, *aliases):
		if self.processsing: return # no need to add aliases during processing
		if len(aliases) == 0:
			if __debug__ and is_debug: aliases = (None,)
			else: return
		if __debug__ and is_debug: debug('project: aliases: ' + str(aliases) + ' ' + str(task.__class__))
		for a in aliases:
			try: self.task_aliases[a].append(task)
			except KeyError: self.task_aliases[a] = [task]

	def tasks_with_aliases(self, task_aliases = None):
		tasks = set()
		if task_aliases is None: task_aliases = (None,)
		try:
			for a in task_aliases: tasks |= set(self.task_aliases[a])
		except KeyError: raise UserReadableException, 'no such task alias: ' + a
		return tasks
		
	def __call__(self, sched_ctx):
		try:
			if self.list_aliases:
				keys = self.task_aliases.keys()
				keys.sort()
				for k in keys:
					if not (__debug__ and is_debug) and k is None: continue
					v = [str(v) for v in self.task_aliases[k]]
					v.sort()
					print (k and str(k) or '<none>') + '\n\t' + '\n\t'.join(v)
			else:
				if self.requested_task_aliases is not None: tasks = self.tasks_with_aliases(self.requested_task_aliases)
				else: tasks = self.task_aliases.get('default', ())
				self.processsing = True
				for x in sched_ctx.parallel_wait(*tasks): yield x
				self.processsing = False
		finally:
			if False and __debug__ and is_debug: print self.persistent
			gc_enabled = gc.isenabled()
			if gc_enabled:
				try: gc.disable()
				except NotImplementedError: pass # jython uses the gc of the jvm
			try:
				path = os.path.join(self.bld_dir.path, 'persistent.pickle')
				if __debug__ and is_debug: t0 = time.time()
				try: f = open(path, 'wb')
				except IOError:
					self.bld_dir.make_dir()
					f = open(path, 'wb')
				try:
					cPickle.dump(abi_sig, f, cPickle.HIGHEST_PROTOCOL)
					cPickle.dump(self.persistent, f, cPickle.HIGHEST_PROTOCOL)
				finally: f.close()
				if __debug__ and is_debug:
					debug('project: pickle: dump time: ' + str(time.time() - t0) + ' s')
					debug('project: pickle: file size: ' + str(int(os.path.getsize(path) * 1000. / (1 << 20)) * .001) + ' MiB')
			finally:
				if gc_enabled: gc.enable()
