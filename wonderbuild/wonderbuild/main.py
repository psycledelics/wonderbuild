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
	from wonderbuild.options import parse_args, validate_options, print_help

	def main():
		import gc
		gc_enabled = gc.isenabled()
		if gc_enabled: gc.disable()
		try:
			options = parse_args(sys.argv[1:])
			option_handlers = set()
			known_options = set()
			help = {}
			
			import logger
			option_handlers.add(logger)
			logger.use_options(options)

			known_options.add('profile')
			if 'help' in options: help['profile'] = ('<file>', 'profile execution and put results in <file>')

			profile = options.get('profile', None)
			
			if profile is None: sys.exit(run(options, known_options, help))
			else:
				import cProfile
				# cProfile is only able to profile one thread
				options['jobs'] = 1 # overrides possible previous jobs options
				cProfile.run('from wonderbuild.main import run; run(options, known_options, help)', profile)
				import pstats
				s = pstats.Stats(profile)
				#s.sort_stats('time').print_stats(45)
				s.sort_stats('cumulative').reverse_order().print_stats()
		finally:
			if gc_enabled: gc.enable()

	def run(options, known_options, help):
		from wonderbuild.project import Project
		project = Project(options)

		script = project.src_node.node_path('wonderbuild_script.py')
		if script.exists:
			d = {}
			execfile('wonderbuild_script.py', d)
			tasks = d['wonderbuild_script'](project)
			usage = False
		else:
			print >> sys.stderr, 'no ' + script.path + ' found'
			usage = True

		if usage or 'help' in options:
			help['help'] = (None, 'show this help and exit')
			help['version'] = (None, 'show the version of this tool and exit')
		
		if 'help' in options:
			project.help(help)
			print_help(help, sys.stdout)
			return 0

		if 'version' in options:
			print 'wonderbuild 0.1'
			return 0
	
		#XXX usage = usage or not validate_options(options, known_options)

		if usage:
			project.help(help)
			print_help(help, sys.stderr)
			return 1

		try: project.process(tasks)
		finally: project.dump()
		return 0
