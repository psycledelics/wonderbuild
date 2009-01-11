#! /usr/bin/env python

if __name__ == '__main__':
	import sys, os, stat, time
	max_time = time.time()
	for i in xrange(1000000):
		try: st = os.stat('.')
		except OSError: sys.exit(1)
		t = st.st_mtime
		if t > max_time: max_time = t
	print max_time		
