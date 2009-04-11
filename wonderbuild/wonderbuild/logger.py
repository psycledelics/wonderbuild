#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import sys, os

known_options = set(['silent', 'verbose'])

def generate_option_help(help):
	help['silent'] = ('<yes|no>', 'suppress printing of informative messages (errors and verbose messages are still printed)', 'no')
	help['verbose'] = ('[zone,...]', 'wonderbuild debugging zones, comma-separated list, or no list for all zones. (example values: exec,cfg,task,sched,fs,project,cpp,...)')

silent = True
is_debug = False
def debug(s): pass

def use_options(options):
	global silent
	if 'silent' in options: silent = options['silent'] != 'no'
	else: silent = False

	if __debug__:
		global is_debug
		is_debug = 'verbose' in options

		if is_debug:
			zones = options['verbose'].split(',')
			global debug
			if len(zones) != 0:
				def debug(s):
					for z in zones:
						if s.startswith(z):
							print >> sys.stderr, colored('35', 'wonderbuild: dbg:') + ' ' + s
							break
			else:
				def debug(s): print >> sys.stderr, colored('35', 'wonderbuild: dbg:') + ' ' + s

out = sys.stdout

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

if os.environ.get('TERM', 'dumb') in ('dumb', 'emacs') or not out.isatty():
	def colored(color, s): return s
else:
	def colored(color, s): return '\33[' + color + 'm' + s + '\33[0m'

