#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import sys, os

if not __debug__:
	is_debug = False
	def debug(s): pass
else:
	from options import options, known_options, help

	known_options.add('--zones')
	help['--zones'] = ('--zones [zones ...]', 'wonderbuild debugging zones (exec, conf, task, sched, fs, project, cpp ...)')

	is_debug = '--zones' in options
	if not is_debug:
		def debug(s): pass
	else:
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
						print >> sys.stderr, colored('35', 'wonderbuild: dbg:') + ' ' + s
						break
		else:
			def debug(s): print >> sys.stderr, colored('35', 'wonderbuild: dbg:') + ' ' + s

out = sys.stdout

if os.environ.get('TERM', 'dumb') in ('dumb', 'emacs') or not out.isatty():
	def colored(color, s):
		return s
else:
	def colored(color, s):
		return '\33[' + color + 'm' + s + '\33[0m'

@property
def cols(): return 80
try: import struct, fcntl, termios
except ImportError: pass
else:
	if out.isatty():
		def _cols():
			lines, cols = struct.unpack(
					"HHHH",
					fcntl.ioctl(
						out.fileno(),
						termios.TIOCGWINSZ,
						struct.pack("HHHH", 0, 0, 0, 0)
					)
				)[:2]
			return cols
		try: _cols() # we try the function once to see if it is suitable
		except IOError: pass
		else: cols = property(_cols)
