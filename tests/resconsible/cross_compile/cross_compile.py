#! /usr/bin/env python

import sys, os
from packages import Packages, Package

packages = Packages()

if __name__ == '__main__':
	for e in ['AR', 'CC', 'CFLAGS', 'CROSS', 'CXX', 'CXXFLAGS', 'EXEEXT', 'LD', 'LIBS', 'NM', 'PKG_CONFIG', 'RANLIB']:
		try: del os.environ[e]
		except KeyError: pass

	sys.path.append(os.getcwd())

	if not os.path.exists('++build'): os.mkdir('++build')
	if not os.path.exists('++install'): os.mkdir('++install')
	os.chdir('++build')

	for n in ['zlib']:
		p = packages.package_by_name(n)
		print p.name(), p.version()
		for d in p.find_deps():
			print d.name(), d.version()
		p.download_deps()
		p.build_deps()

