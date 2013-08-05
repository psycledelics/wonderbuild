#! /usr/bin/env python

if __name__ == '__main__':
	class X(object):
		__slots__ = ('a',)
		
		def __init__(self):
			self.a = 0

		def f(self): return self.a

		@property
		def p(self): return self.a

	import time
	import gc; gc.disable()
	x = X()
	count = 1000000
	count2 = 4
	
	t0 = time.time()
	for i in xrange(count2):
		for j in xrange(count): x.a
	print time.time() - t0
	
	t0 = time.time()
	for i in xrange(count2):
		for j in xrange(count): x.f()
	print time.time() - t0
	
	t0 = time.time()
	for i in xrange(count2):
		for j in xrange(count): x.p
	print time.time() - t0
