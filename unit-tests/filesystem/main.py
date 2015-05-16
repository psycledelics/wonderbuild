#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2013-2015 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>


##############################################################################
#
# this script tests the filesystem cache
#
##############################################################################


if __name__ == '__main__':
	try: import wonderbuild
	except ImportError:
		import sys, os
		dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
		if dir not in sys.path: sys.path.append(dir)
		try: import wonderbuild
		except ImportError:
			print >> sys.stderr, 'could not import wonderbuild module with path', sys.path
			sys.exit(1)

	import time
	from wonderbuild.filesystem import FileSystem

	persistent = {}
	fs = FileSystem(persistent)
	for i in xrange(2):
		t0 = time.time()
		files = []
		for x in (fs.root / 'usr' / 'include').find_iter(('*.h', '*.hpp')):
			files.append(x.sig)
		for x in (fs.root / 'usr' / 'lib').find_iter(('*.so', '*.so.*'), prune_pats=('private','llvm-*')): # perm denied and cycling symlinks
			files.append(x.sig)
		t1 = time.time()
		print '{} files in {:6.2f} seconds: {:10.0f} f/s'.format(len(files), t1 - t0, len(files) / (t1 - t0))

