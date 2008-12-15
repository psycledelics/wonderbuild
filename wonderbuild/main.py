#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

def run():
	from project import Project
	project = Project()

	d = {}
	execfile('wonderbuild_script.py', d, d)
	tasks = d['wonderbuild_script'](project)

	from options import options, known_options, help
	help['--version'] = ('--version', 'show the version of this tool and exit')

	if '--help' in options:
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
			if len(h) >= 3: print ''.ljust(just), '(default: ' + h[2] + ')'
		return

	if '--version' in options:
		print 'wonderbuild 0.1'
		return

	project.options()
	for o in options:
		if o.startswith('-'):
			e = o.find('=')
			if e >= 0: o = o[:e]
			if o not in known_options: raise Exception, 'unknown option: ' + o

	project.conf()
	project.build(tasks)
	project.dump()

def main():
	#import gc; gc.disable()

	from options import options, known_options, help
	known_options.add('--profile')
	help['--profile'] = ('--profile', 'profile wonderbuild execution')

	if '--profile' in options:
		import cProfile, pstats
		cProfile.run('run()', '/tmp/profile')
		p = pstats.Stats('/tmp/profile')
		p.sort_stats('cumulative').reverse_order().print_stats()
	else: run()

if __name__ == '__main__': main()
