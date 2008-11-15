#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

if __name__ == '__main__':

	import os, os.path, cPickle, time, timeit

	def timed(func, *args, **kw):
		t0 = time.time()
		func(*args, **kw)
		print func.__name__, time.time() - t0

	def load(path):
		f = file(path, 'rb')
		p = cPickle.Unpickler(f)
		t0 = time.time()
		d = p.load()
		print 'load:', time.time() - t0
		f.close()
		return d

	def dump(d, path):
		f = file(path, 'wb')
		p = cPickle.Pickler(f, cPickle.HIGHEST_PROTOCOL)
		t0 = time.time()
		p.dump(d)
		print 'dump:', time.time() - t0
		f.close()

	def test(X):
		path = '/tmp/t'
		count = 1000000
		d = {}
		for x in xrange(count): d[x] = X(x, x)
		print X.__name__;
		dump(d, path);
		d = load(path)
		for x in xrange(count):
			assert d[x].a == x
			#assert d[x].b == x
		print 'size:', os.path.getsize(path)

	class OneElementDict(object):
		def __init__(self, a, b): self.a = a
	test(OneElementDict)

	class OneSlotDict(object):
		__slots__ = ('a',)
		def __init__(self, a, b): self.a = a
	test(OneSlotDict)
	
	class TwoSlotsDict(object):
		__slots__ = ('a', 'b')
		def __init__(self, a, b): self.a = a; self.b = b
	test(TwoSlotsDict)
	
	class TwoSlotsTuple(object):
		__slots__ = ('a', 'b')
		def __init__(self, a, b): self.a = a; self.b = b
		def __getstate__(self): return self.a, self.b
		def __setstate__(self, data): self.a, self.b = data
	test(TwoSlotsTuple)
