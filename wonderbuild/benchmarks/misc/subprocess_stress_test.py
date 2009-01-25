#! /usr/bin/env python

if __name__ == '__main__':

	import threading, subprocess, time
	
	thread_count = 2
	input = 'test\n'
	args = ['cat']
	
	lock = threading.Lock() # workaround for bug still present in python 2.5.2
	
	def thread_function(input, args):
		while True:
			if input is not None: # workaround for bug still present in python 2.5.2
				lock.acquire()
				try: p = subprocess.Popen(
						args = args,
						bufsize = -1,
						stdin = subprocess.PIPE,
						stdout = subprocess.PIPE,
						stderr = subprocess.PIPE,
					)
				finally: lock.release()
			else: p = subprocess.Popen(
					args = args,
					bufsize = -1,
					stdin = None,
					stdout = subprocess.PIPE,
					stderr = subprocess.PIPE,
				)
			out, err = p.communicate(input)
			print p.returncode, time.time()

	threads = []
	for i in xrange(thread_count):
		t = threading.Thread(target = thread_function, args = (input, args), name = 'thread-' + str(i))
		#t.daemon = True
		t.setDaemon(True)
		t.start()
		threads.append(t)
		
	for t in threads: t.join(timeout = 3600.0)
