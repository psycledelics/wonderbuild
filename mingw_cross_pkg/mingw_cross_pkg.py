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
		package_names = []
		continue_build = False
		rebuild = False
		no_act = False
		for arg in args:
			if arg.startswith('-'):
				if arg == '--continue': continue_build = True
				elif arg == '--rebuild': rebuild = True
				elif arg == '--no-act': no_act = True
				else:
					sys.stderr.write(sys.argv[0] + ': unrecognised option: ' + arg + '\n')
					sys.stderr.write('usage: install [--continue | --rebuild | --no-act] <package...>\n')
					sys.exit(2)
			else: package_names.append(arg)
		if no_act: packages.install_no_act(package_names)
		else: packages.install(package_names, continue_build = continue_build, rebuild = rebuild)
	elif command == 'remove':
		package_names = []
		verbose = False
		for arg in args:
			if arg.startswith('-'):
				if arg == '--verbose': verbose = True
				else:
					sys.stderr.write(sys.argv[0] + ': unrecognised option: ' + arg + '\n')
					sys.stderr.write('usage: remove [--verbose] <package...>\n')
					sys.exit(2)
			else: package_names.append(arg)
		packages.remove(package_names, verbose)
	else:
		sys.stderr.write(sys.argv[0] + ': unrecognised command: ' + command + '\n')
		usage()
		sys.exit(1)
