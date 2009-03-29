#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import sys

class OptionHandler(object):
	known_options = set()

	@staticmethod
	def help(help): pass

class Options(object): pass

def parse_args(args = None):
	if args is None: args = sys.argv[1:]
	options = {}
	for a in args:
		if a.startswith('--'): d = 2
		elif a.startswith('-'): d = 1
		else: d = 0
		e = a.find('=')
		if e >= 0:
			k = a[d:e]
			v = a[e + 1:]
		else:
			k = a[d:]
			v = ''
		options[k] = v
	return options

def validate_options(options, known_options):
	ok = True
	for o in options:
			if o not in known_options:
				print >> sys.stderr, 'unknown option: ' + o
				ok = False
	return ok

def print_help(help, out):
	keys = []
	def name(k, v):
		if v is None: v = k
		else: v = k + '=' + v
		v = '--' + v
		return v
	just = 0
	for k, v in help.iteritems():
		v = name(k, v[0])
		if len(v) > just: just = len(v)
		keys.append(k)
	keys.sort()
	just += 1
	for k in keys:
		v = help[k]
		print >> out, name(k, v[0]).ljust(just), v[1]
		if len(v) >= 3: print >> out, ''.ljust(just), '(default: ' + v[2] + ')'
