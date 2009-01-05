#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import sys
from optparse import OptionParser

parser = OptionParser()

options = sys.argv[1:]

known_options = set()

help = {}

def validate_options():
	ok = True
	for o in options:
		if o.startswith('-'):
			e = o.find('=')
			if e >= 0:
				if o[:e + 1] in known_options: continue
				o = o[:e]
			if o in known_options: continue
			print >> sys.stderr, 'unknown option: ' + o
			ok = False
	return ok

