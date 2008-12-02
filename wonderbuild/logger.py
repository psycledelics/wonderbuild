#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from options import options

is_debug = __debug__ and '--debug' in options
if is_debug:
	import sys
	def debug(s): print >> sys.stderr, s
else:
	def debug(s): pass
