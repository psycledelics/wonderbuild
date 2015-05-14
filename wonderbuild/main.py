#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2010 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import sys, os

if __name__ == '__main__':
	dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
	if dir not in sys.path: sys.path.append(dir)
	from wonderbuild.main import main
	main()
else:
	from wonderbuild import UserReadableException
	from wonderbuild.logger import out, colored, cols
	from wonderbuild.options import parse_args, validate_options, print_help, OptionCollector

	def main():
		r = 1
		try:
			import time, gc
			t = time.time()
			gc_enabled = gc.isenabled()
			if gc_enabled:
				try: gc.disable()
				except NotImplementedError: pass # jython uses gc of the jvm
			try:
				options = parse_args(sys.argv[1:])
				option_collector = OptionCollector()
	
				import logger
				logger.use_options(options)
				option_collector.option_decls.add(logger)

				import subprocess_wrapper
				subprocess_wrapper.use_options(options)
				option_collector.option_decls.add(subprocess_wrapper)

				option_collector.known_options.add('debug')
				if 'help' in options: option_collector.help['debug'] = ('[passwd]', 'use the python rpdb2/winpdb debugger', 'prompt for password if none given')
				debug = options.get('debug', None)
				if debug is not None:
					import rpdb2
					if len(debug) != 0: rpdb2.start_embedded_debugger(debug)
					else:
						print 'wonderbuild: please chose a password for the python rpdb2 debugger:'
						rpdb2.start_embedded_debugger_interactive_password()

				option_collector.known_options.add('profile')
				if False: # do not show this option
					if 'help' in options: option_collector.help['profile'] = ('<file>', 'profile execution and put results in <file> (implies --jobs=1)')
				profile = options.get('profile', None)
				if profile is None: r = run(options, option_collector)
				else:
					import cProfile
					cProfile.run(
'''
from wonderbuild.main import run
from wonderbuild.options import parse_args, OptionCollector
options = parse_args(sys.argv[1:])
option_collector = OptionCollector()
option_collector.known_options.add('profile')
# cProfile is only able to profile one thread
options['jobs'] = 1 # overrides possible previous jobs options
run(options, option_collector)
''',
						profile
					)
					import pstats
					s = pstats.Stats(profile)
					#s.sort_stats('time').print_stats(45)
					s.sort_stats('cumulative').reverse_order().print_stats()
					r = 0
			finally:
				t = time.time() - t
				print >> sys.stderr, colored('2', 'wonderbuild: build time: ' + str(t) + 's')
				if gc_enabled: gc.enable()
		except UserReadableException, e:
			print >> sys.stderr, colored('31;1', 'wonderbuild: failed: ') + colored('31', str(e))
			r = 1
		else:
			if r != 0: print >> sys.stderr, colored('31;1', 'wonderbuild: failed: ') + colored('31', 'nonzero return code: ' + str(r))
		if r != 0: sys.stderr.write('\a')
		sys.exit(r)

	def run(options, option_collector):
		if 'version' in options:
			from wonderbuild import version
			print 'wonderbuild ' + '.'.join(str(v) for v in version)
			return 0

		from wonderbuild.task import Task
		class MainTask(Task):
			def __init__(self, project):
				Task.__init__(self)
				self.project = project

			def __call__(self, sched_ctx):
				self.result = 1
				
				from wonderbuild.script import ScriptLoaderTask, default_script_file
				script = self.project.top_src_dir / default_script_file
				if script.exists:
					script_loader_task = ScriptLoaderTask.shared(self.project, script)
					for x in sched_ctx.parallel_wait(script_loader_task): yield x
					if 'help' not in options:
						option_collector.consolidate_known_options()
						usage_error = not validate_options(options, option_collector.known_options)
					else: usage_error = False
				else:
					usage_error = 'help' not in options
					if usage_error:
						print >> sys.stderr, 'wonderbuild: error: no ' + script.path + ' found'
					option_collector.consolidate_known_options()
				
				if usage_error or 'help' in options:
					option_collector.help['help'] = (None, 'show this help and exit')
					option_collector.help['version'] = (None, 'show the version of this tool and exit')
					option_collector.consolidate_help()
					print_help(option_collector.help, out, cols)
					self.result = usage_error and 1 or 0
					return

				self.project.task_aliases['default'] = script_loader_task.script_task.default_tasks
				for x in sched_ctx.parallel_wait(self.project): yield x
				
				self.result = 0

		from wonderbuild.scheduler import Scheduler
		option_collector.option_decls.add(Scheduler)

		try:
			from wonderbuild.project import Project
			project = Project(options, option_collector)
			main_task = MainTask(project)
		except:
			option_collector.consolidate_known_options()
			validate_options(options, option_collector.known_options)
			raise

		try: Scheduler(**options).process(main_task)
		except:
			project.global_purge = False # some task failed, so not all the tasks have been evaluated => we shouldn't do the global purge
			raise
		finally: project.dump_persistent()

		return main_task.result
