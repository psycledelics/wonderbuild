#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import sys, os, os.path, time, filesystem, cxx_preprocessor

if __name__ == '__main__':
	tree = filesystem.Tree()
	scanner = cxx_preprocessor.CppDumbIncludeScanner()

	t0 = time.time()
	tree.load()
	print >> sys.stderr, 'load time:', time.time() - t0
	
	top = tree.find(os.curdir)

	src = top.find('src')
	scanner.paths.append(src.abs_path)
	
	foo = src.find('foo/foo.cpp')
	print foo.abs_path
	for dep in scanner.scan_deps(foo.abs_path):
		dep = src.find(dep)
		print '\t', dep.abs_path
	
	main = src.find('main/main.cpp')
	print main.abs_path
	for dep in scanner.scan_deps(main.abs_path):
		dep = src.find(dep)
		print '\t', dep.abs_path
	
	tree.display()

	t0 = time.time()
	tree.dump()
	print >> sys.stderr, 'dump time:', time.time() - t0

	scanner._cache().save()
