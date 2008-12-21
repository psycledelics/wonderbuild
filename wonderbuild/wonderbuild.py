#! /usr/bin/env python

if __name__ == '__main__':
	import sys, os
	if True:
		dir = os.path.abspath(os.path.dirname(sys.argv[0]))
		if dir not in sys.path: sys.path.append(dir)
		from wonderbuild.main import main
		main()
	else:
		d = {}
		execfile(os.path.join(os.path.dirname(sys.argv[0]), 'wonderbuild', 'main.py'), d, d)
		d['main']()
