#! /usr/bin/env python

if __name__ == '__main__':
	import sys, os, stat, time
	max_time = time.time()
	
	for i in xrange(200):
		for lib in xrange(50):
			for cpp in xrange(100):
				path = '../../bench/lib_' + str(lib) + '/class_' + str(cpp) + '.cpp'
				try: st = os.stat(path)
				except OSError: sys.exit(1)
				t = st.st_mtime
				if t > max_time: max_time = t
	print max_time
