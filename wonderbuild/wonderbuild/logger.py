#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import sys, os

from options import options, known_options, help

known_options.add('--silent')
help['--silent'] = ('--silent', 'suppress progress output (errors and debugging messages are still printed)')

silent = '--silent' in options

if not __debug__:
	is_debug = False
	def debug(s): pass
else:
	known_options.add('--zones')
	help['--zones'] = ('--zones=[zone,...]', 'wonderbuild debugging zones, comma-separated list, or no list for all zones. (example values: exec,cfg,task,sched,fs,project,cpp,...)')

	zones = None
	for o in options:
		if o == '--zones':
			zones = []
			break
		if o.startswith('--zones='):
			o = o[len('--zones='):]
			if len(o): zones = o.split(',')
			else: zones = []
			break
	is_debug = zones is not None
	if not is_debug:
		del zones
		is_debug = False
		def debug(s): pass
	elif len(zones):
		def debug(s):
			for z in zones:
				if s.startswith(z):
					print >> sys.stderr, colored('35', 'wonderbuild: dbg:') + ' ' + s
					break
	else:
		del zones
		def debug(s): print >> sys.stderr, colored('35', 'wonderbuild: dbg:') + ' ' + s

out = sys.stdout

if os.environ.get('TERM', 'dumb') in ('dumb', 'emacs') or not out.isatty():
	def colored(color, s): return s
else:
	def colored(color, s): return '\33[' + color + 'm' + s + '\33[0m'

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
