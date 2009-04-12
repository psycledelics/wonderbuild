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

			import logger
			logger.use_options(options)

			option_collector = OptionCollector()
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
		from wonderbuild.project import Project
		project = Project(options, option_collector)

		script = project.src_node / 'wonderbuild_script.py'
		if script.exists:
			d = {}
			execfile(script.path, d)
			tasks = d['wonderbuild_script'](project, script.parent)
			usage = False
		else:
			print >> sys.stderr, 'no ' + script.path + ' found'
			usage = True

		if usage or 'help' in options:
			option_collector.help['help'] = (None, 'show this help and exit')
			option_collector.help['version'] = (None, 'show the version of this tool and exit')
			option_collector.consolidate_help()
		
		if 'help' in options:
			print_help(option_collector.help, sys.stdout)
			return 0

		if 'version' in options:
			print 'wonderbuild 0.2'
			return 0
	
		if not usage:
			option_collector.consolidate_known_options()
			usage = not validate_options(options, option_collector.known_options)

		if usage:
			print_help(option_collector.help, sys.stderr)
			return 1

		try: project.process(tasks)
		finally: project.dump()
		return 0
