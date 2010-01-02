#! /usr/bin/env python

if __name__ == '__main__':

	import sys, os, errno, stat, time

	path = '/tmp/test'

	while True:
		file = open(path, 'wb')
		file.write('test')
		file.close()
		print 'wrote: ' + path
		old_time = 0
		time0 = time.time()
		while time.time() - time0 < 1:
			try: st = os.stat(path)
			except OSError, e:
				if e.errno != errno.ENOENT: raise
				st = os.lstat(path)
			new_time = st.st_mtime
			if old_time == 0:
				if time0 > new_time: print 'time difference: ' + str(new_time - time0)
			else:
				if old_time != new_time: print 'time changed: old: ' + str(old_time) + ', new: ' + str(new_time)
			old_time = new_time

