#! /usr/bin/env python

import sys
from packages import Packages, Package

packages = Packages()

def usage():
	sys.stderr.write('usage: ' + sys.argv[0] + ' <command> [args]\n')
	sys.stderr.write('where <command> is one of: help, version, list, install, remove\n')

if __name__ == '__main__':
	if len(sys.argv) < 2:
		usage()
		sys.exit(1)
	command = sys.argv[1]
	args = sys.argv[2:]
	if command == 'version' or command == '--version' or command == '-v': sys.stdout.write('0.1\n')
	elif command == 'help' or command == '--help' or command == '-h' or command == '-?': usage()
	elif command == 'list': packages.list()
	elif command == 'install':
		targets = []
		continue_build = False
		rebuild = False
		for arg in args:
			if arg.startswith('-'):
				if arg == '--continue': continue_build = True
				elif arg == '--rebuild': rebuild = True
				else:
					sys.stderr.write(sys.argv[0] + ': unrecognised option: ' + arg + '\n')
					sys.stderr.write('usage: install [--continue | --rebuild] <target...>\n')
					sys.exit(2)
			else: targets.append(arg)
		packages.build(targets, continue_build = continue_build, rebuild = rebuild)
	elif command == 'remove': packages.remove(args)
	else:
		sys.stderr.write(sys.argv[0] + ': unrecognised command: ' + command + '\n')
		usage()
		sys.exit(1)
