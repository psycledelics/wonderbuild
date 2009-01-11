#! /usr/bin/env python

if __name__ == '__main__':
	class X(object):
		__slots__ = ('_x1', '_x2', '_x3', '_x4', '_x5')
		
		def __init__(self):
			self._x2 = self._x3 = None
		
		def x1(self):
			try: return self._x1
			except AttributeError:
				self._x1 = 0
				return self._x1

		def x2(self):
			if self._x2 is not None: return self._x2
			self._x2 = 0
			return self._x2

		def x3(self):
			if self._x3 is None: self._x3 = 0
			return self._x3

		def x4(self):
			if hasattr(self, '_x4'): return self._x4
			self._x4 = 0
			return self._x4
		
		def x5(self):
			if not hasattr(self, '_x5'): self._x5 = 0
			return self._x5

	import time
	import gc; gc.disable()
	x = X()
	count = 1000000
	count2 = 4
	
	def measure(x):
		t0 = time.time()
		for i in xrange(count2):
			for j in xrange(count): x()
		print time.time() - t0
	
	for x in (x.x1, x.x2, x.x3, x.x4, x.x5): measure(x)
