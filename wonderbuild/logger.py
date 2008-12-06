#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

if not __debug__:
	is_debug = False
	def debug(s): pass
else:
	from options import options, help

	help['--zones'] = ('--zones [zones ...]', 'wonderbuild debugging zones (sched, fs, ...)')

	is_debug = '--zones' in options
	if not is_debug:
		def debug(s): pass
	else:
		import sys
		zones = []
		i = options.index('--zones')
		l = len(options)
		i += 1
		while i < l:
			o = options[i]
			if o.startswith('-'): break
			zones.append(o)
			i += 1
		if len(zones):
			def debug(s):
				for z in zones:
					if s.startswith(z):
						print >> sys.stderr, s
						break
		else:
			def debug(s): print >> sys.stderr, s
