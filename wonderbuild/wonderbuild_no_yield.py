#! /usr/bin/env python

if __name__ == '__main__':
	import sys, os
	if True:
		dir = os.path.abspath(os.path.dirname(__file__))
		if dir not in sys.path: sys.path.append(dir)
		from wonderbuild_no_yield.main import main
		main()
	else:
		d = {}
		execfile(os.path.join(os.path.dirname(__file__), 'wonderbuild_no_yield', 'main.py'), d, d)
		d['main']()
