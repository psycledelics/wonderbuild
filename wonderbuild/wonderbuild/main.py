#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import sys, os
	
def run():
	from project import Project
	project = Project()

	if os.path.exists('wonderbuild_script.py'):
		d = {}
		execfile('wonderbuild_script.py', d)
		tasks = d['wonderbuild_script'](project)
		usage = False
	else:
		print >> sys.stderr, 'no wonderbuild_script.py found'
		usage = True

	from options import options, known_options, help
	help['--version'] = ('--version', 'show the version of this tool and exit')

	def print_help(out):
		help['--help'] = ('--help', 'show this help and exit')

		project.help()
		keys = []
		just = 0
		for k, v in help.iteritems():
			if len(v[0]) > just: just = len(v[0])
			keys.append(k)
		keys.sort()
		just += 1
		for h in keys:
			h = help[h]
			print h[0].ljust(just), h[1]
			if len(h) >= 3: print >> out, ''.ljust(just), '(default: ' + h[2] + ')'

	if '--help' in options:
		print_help(sys.stdout)
		return 0

	if '--version' in options:
		print 'wonderbuild 0.1'
		return 0
	
	project.options()
	for o in options:
		if o.startswith('-'):
			e = o.find('=')
			if e >= 0: o = o[:e]
			if o not in known_options:
				print >> sys.stderr, 'unknown option: ' + o
				usage = True

	if usage:
		print_help(sys.stderr)
		return 1

	project.configure()
	project.build(tasks)
	project.dump()
	return 0

def main():
	import gc
	gc_enabled = gc.isenabled()
	if gc_enabled: gc.disable()
	try:
		from options import options, known_options, help
		known_options.add('--profile')
		help['--profile'] = ('--profile', 'profile wonderbuild execution')

		if '--profile' in options:
			import cProfile, pstats
			cProfile.run('sys.exit(run())', '/tmp/profile')
			p = pstats.Stats('/tmp/profile')
			p.sort_stats('cumulative').reverse_order().print_stats()
		else: sys.exit(run())
	finally:
		if gc_enabled: gc.enable()

if __name__ == '__main__':
	dir = os.path.abspath(os.path.dirname(os.path.dirname(sys.argv[0])))
	if dir not in sys.path: sys.path.append(dir)
	main()
