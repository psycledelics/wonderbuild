#! /usr/bin/env python

if __name__ == '__main__':

	import os, threading, time

	if True: import subprocess
	else: import pproc as subprocess
	
	thread_count = 2
	if True: input = 'test\n'; args = ['cat']
	else: input = 'int main() { return 0; }\n'; args = ['c++', '-xc++', '-', '-o', os.devnull]

	def thread_function(input, args):
		while True:
			p = subprocess.Popen(
				args = args,
				bufsize = -1,
				stdin = input and subprocess.PIPE,
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
