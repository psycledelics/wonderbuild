#! /usr/bin/env python

if __name__ == '__main__':
	import sys, os
	dir = os.path.abspath(os.path.dirname(sys.argv[0]))
	if not dir in sys.path: sys.path.append(dir)
	from wonderbuild.main import main
	main()
