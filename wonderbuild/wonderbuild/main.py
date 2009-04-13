#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import sys, os

if __name__ == '__main__':
	dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
	if dir not in sys.path: sys.path.append(dir)
	from wonderbuild.main import main
	main()
else:
	from wonderbuild.options import parse_args, validate_options, print_help, OptionCollector

	def main():
		import gc
		gc_enabled = gc.isenabled()
		if gc_enabled: gc.disable()
		try:
			options = parse_args(sys.argv[1:])
			option_collector = OptionCollector()

			import logger
			logger.use_options(options)
			option_collector.option_decls.add(logger)

			option_collector.known_options.add('profile')
			if 'help' in options: option_collector.help['profile'] = ('<file>', 'profile execution and put results in <file> (implies --jobs=1)')
			profile = options.get('profile', None)
			if profile is None: sys.exit(run(options, option_collector))
			else:
				import cProfile
				# cProfile is only able to profile one thread
				options['jobs'] = 1 # overrides possible previous jobs options
				cProfile.run('from wonderbuild.main import run; run(options, option_collector)', profile)
				import pstats
				s = pstats.Stats(profile)
				#s.sort_stats('time').print_stats(45)
				s.sort_stats('cumulative').reverse_order().print_stats()
		finally:
			if gc_enabled: gc.enable()

	def run(options, option_collector):
		if 'version' in options:
			print 'wonderbuild 0.3'
			return 0

		from wonderbuild.task import Task
		class MainTask(Task):
			def __init__(self, project):
				Task.__init__(self)
				self.project = project
				
			def __call__(self, sched_context):
				sched_context.parallel_wait(self.project)
				
				from wonderbuild.script import default_script_file
				script = self.project.top_src_dir / default_script_file
				if script.exists:
					script_tasks = (self.project.script_task(script),)
					usage_error = False
				else:
					print >> sys.stderr, 'wonderbuild: no ' + script.path + ' found'
					script_tasks = ()
					usage_error = True

				if not usage_error and 'help' not in options:
					sched_context.parallel_wait(*script_tasks)
					option_collector.consolidate_known_options()
					usage_error = not validate_options(options, option_collector.known_options)

				if usage_error or 'help' in options:
					sched_context.parallel_wait(*script_tasks)
					option_collector.help['help'] = (None, 'show this help and exit')
					option_collector.help['version'] = (None, 'show the version of this tool and exit')
					option_collector.consolidate_help()
					print_help(option_collector.help, sys.stdout)
					self.result = usage_error and 1 or 0
					return

				self.project.process_tasks_by_aliases()
				self.result = 0

		from wonderbuild.project import Project
		main_task = MainTask(Project(options, option_collector))

		from wonderbuild.scheduler import Scheduler
		option_collector.option_decls.add(Scheduler)
		Scheduler(options).process([main_task])

		return main_task.result
