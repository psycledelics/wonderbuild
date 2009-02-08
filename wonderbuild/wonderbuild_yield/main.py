#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import sys, os

if __name__ == '__main__':
	dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
	if dir not in sys.path: sys.path.append(dir)
	from wonderbuild_yield.main import main
	main()
else:
	from wonderbuild_yield.options import options, validate_options, known_options, help, print_help

	def main():
		import gc
		gc_enabled = gc.isenabled()
		if gc_enabled: gc.disable()
		try:
			known_options.add('--profile=')
			help['--profile='] = ('--profile=<file>', 'profile execution and put results in <file>')
		
			profile = None
			for o in options:
				if o.startswith('--profile='):
					profile = o[len('--profile='):]
					break
			
			if profile is None: sys.exit(run())
			else:
				import cProfile
				# cProfile is only able to profile one thread
				options.append('--jobs=1') # overrides possible previous --jobs options
				cProfile.run('from wonderbuild_yield.main import run; run()', profile)
				import pstats
				s = pstats.Stats(profile)
				#s.sort_stats('time').print_stats(45)
				s.sort_stats('cumulative').reverse_order().print_stats()
		finally:
			if gc_enabled: gc.enable()

	def run():
		from wonderbuild_yield.project import Project
		project = Project()

		script = project.src_node.node_path('wonderbuild_script.py')
		if script.exists:
			d = {}
			execfile('wonderbuild_script.py', d)
			tasks = d['wonderbuild_yield_script'](project)
			usage = False
		else:
			print >> sys.stderr, 'no ' + script.path + ' found'
			usage = True

		help['--version'] = ('--version', 'show the version of this tool and exit')

		if '--help' in options:
			project.help()
			print_help(sys.stdout)
			return 0

		if '--version' in options:
			print 'wonderbuild 0.1-yield'
			return 0
	
		project.options()
		usage = not validate_options()

		if usage:
			project.help()
			print_help(sys.stderr)
			return 1

		try: project.process(tasks)
		finally: project.dump()
		return 0
