#! /usr/bin/env python

import sys
from packages import Packages, Package

packages = Packages()

def usage():
	print 'usage:', sys.argv[0], '<command> [args]'
	print 'where <command> is one of: list, build'
	sys.exit(1)

if __name__ == '__main__':
	if len(sys.argv) < 2: usage()
				
	command = sys.argv[1]
	args = sys.argv[2:]
	if command == 'list': packages.list()
	elif command == 'build': packages.build(args)
	else: usage()
