#! /usr/bin/env python

import sys
from packages import Packages, Package

version = '0.1'

packages = Packages()

commands = ['help', 'version', 'list', 'show', 'install', 'remove', 'reverse-depends', 'clean-build']

def usage(out = sys.stderr, command = None):
	if command is None:
		out.write('Usage: ' + sys.argv[0] + ' <command> [args]\n')
		out.write('  where <command> is one of: ' + ', '.join(commands) + '.\n')
		out.write('\n')
	if command is None or command == 'help':
		out.write('Usage: <help | --help> [command]\n')
		out.write('or   : <command> --help\n')
		out.write('  gives help on command, or on all commands.\n')
		if command == 'help': out.write('  where [command] is one of: ' + ', '.join(commands) + '.\n')
		out.write('\n')
	if command is None or command == 'version':
		out.write('Usage: <version | --version>\n')
		out.write('  prints the version of this tool.\n')
		out.write('\n')
	if command is None or command == 'list':
		out.write('Usage: list\n')
		out.write('  gives a list of all packages, with state information.\n')
		out.write('\n')
	if command is None or command == 'show':
		out.write('Usage: show <package...>\n')
		out.write('  shows the details of the packages.\n')
		out.write('\n')
	if command is None or command == 'install':
		out.write('Usage: install [--continue | --rebuild | --no-download | --no-act] <package...>\n')
		out.write('  installs the packages, and their dependencies.\n')
		out.write('  Packages given as arguments will be marked as user, unless the --rebuild option is present.\n')
		out.write('  --no-act         do not really install, just show what would be done.\n')
		out.write('  --skip-download  skip the download step.\n')
		out.write('  --rebuild        rebuild the packages given as arguments.\n')
		out.write('  --continue       continue after a build failure.\n')
		out.write('\n')
	if command is None or command == 'remove':
		out.write('Usage: remove [--verbose | --no-act] <package...>\n')
		out.write('  removes the packages, dependent packages, and packages marked auto that become no longer needed.\n')
		out.write('  --no-act   do not really remove, just show what would be done.\n')
		out.write('  --verbose  show what files and dirs are removed.\n')
		out.write('\n')
	if command is None or command == 'reverse-depends':
		out.write('Usage: reverse-depends [--installed-only] <package...>\n')
		out.write('  shows the reverse dependencies of the packages.\n')
		out.write('  --installed-only  only show installed packages.\n')
		out.write('\n')
	if command is None or command == 'clean-build':
		out.write('Usage: clean-build [--download | --destdir | --all] <package...>\n')
		out.write('  cleans the build dirs of packages.\n')
		out.write('  --dest-dir  also clean the dest dir.\n')
		out.write('  --download  also clean the downloaded files.\n')
		out.write('  --all       wipe out the whole build dir altogether (same effect as --dest-dir --download).\n')
		out.write('\n')

if __name__ == '__main__':
	if len(sys.argv) < 2:
		usage()
		sys.exit(1)
	command = sys.argv[1]
	args = sys.argv[2:]
	if '--help' in args and command in commands:
		usage(command = command)
	elif command == 'version' or command == '--version' or '--version' in args:
		sys.stdout.write(version)
		sys.stdout.write('\n')
	elif command == 'help' or command == '--help':
		command = None
		if len(args):
			command = args[0]
			if not command in commands:
				sys.stderr.write(sys.argv[0] + ': unrecognised command: ' + command + '\n')
				usage(command = 'help')
				sys.exit(2)
		else: command = None
		usage(sys.stdout, command)
	elif command == 'list':
		if len(args):
			usage(command = 'list')
			sys.exit(2)
		packages.list()
	elif command == 'install':
		package_names = []
		continue_build = False
		rebuild = False
		skip_download = False
		no_act = False
		for arg in args:
			if arg.startswith('-'):
				if arg == '--continue': continue_build = True
				elif arg == '--rebuild': rebuild = True
				elif arg == '--skip-download': skip_download = True
				elif arg == '--no-act': no_act = True
				else:
					sys.stderr.write(sys.argv[0] + ': unrecognised option: ' + arg + '\n')
					usage(command = 'install')
					sys.exit(2)
			else: package_names.append(arg)
		if no_act: packages.install_no_act(package_names)
		else: packages.install(package_names, continue_build = continue_build, rebuild = rebuild, skip_download = skip_download)
	elif command == 'remove':
		package_names = []
		verbose = False
		no_act = False
		for arg in args:
			if arg.startswith('-'):
				if arg == '--verbose': verbose = True
				elif arg == '--no-act': no_act = True
				else:
					sys.stderr.write(sys.argv[0] + ': unrecognised option: ' + arg + '\n')
					usage(command = 'remove')
					sys.exit(2)
			else: package_names.append(arg)
		if no_act: packages.remove_no_act(package_names)
		else: packages.remove(package_names, verbose)
	elif command == 'reverse-depends':
		package_names = []
		installed_only = False
		for arg in args:
			if arg.startswith('-'):
				if arg == '--installed-only': installed_only = True
				else:
					sys.stderr.write(sys.argv[0] + ': unrecognised option: ' + arg + '\n')
					usage(command = 'reverse-depends')
					sys.exit(2)
			else: package_names.append(arg)
		packages.print_reverse_deps(package_names, installed_only)
	elif command == 'show':
		package_names = []
		for arg in args:
			if arg.startswith('-'):
				sys.stderr.write(sys.argv[0] + ': unrecognised option: ' + arg + '\n')
				usage(command = 'show')
				sys.exit(2)
			else: package_names.append(arg)
		packages.show(package_names)
	elif command == 'clean-build':
		package_names = []
		all = False
		dest_dir = False
		download = False
		for arg in args:
			if arg.startswith('-'):
				if arg == '--dest-dir': dest_dir = True
				elif arg == '--download': download = True
				elif arg == '--all': all = True
				else:
					sys.stderr.write(sys.argv[0] + ': unrecognised option: ' + arg + '\n')
					usage(command = 'clean-build')
					sys.exit(2)
			else: package_names.append(arg)
		packages.clean_build(package_names, all = all, dest_dir = dest_dir, download = download)
	else:
		sys.stderr.write(sys.argv[0] + ': unrecognised command: ' + command + '\n')
		usage()
		sys.exit(1)
