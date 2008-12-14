#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

if __name__ == '__main__':

	import os, cPickle, gc, time

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
		gc.disable()
		path = '/tmp/t'
		count = 500000
		d = {}
		for x in xrange(count): d[x] = X(x, x)
		print X.__name__;
		dump(d, path);
		print 'size:', os.path.getsize(path)
		d = load(path)
		for x in xrange(count):
			assert d[x].a == x
			#assert d[x].b == x
		gc.enable()

	class OneElementDict(object):
		def __init__(self, a, b): self.a = a
	test(OneElementDict)

	class OneSlot(object):
		__slots__ = ('a',)
		def __init__(self, a, b): self.a = a
	test(OneSlot)
	
	class TwoSlots(object):
		__slots__ = ('a', 'b')
		def __init__(self, a, b): self.a = a; self.b = b
	test(TwoSlots)
	
	class TwoSlotsTuple(object):
		__slots__ = ('a', 'b')
		def __init__(self, a, b): self.a = a; self.b = b
		def __getstate__(self): return self.a, self.b
		def __setstate__(self, data): self.a, self.b = data
	test(TwoSlotsTuple)
	
	class ManySlotsTuple(object):
		__slots__ = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z')
		def __init__(self, a, b): self.a = a; self.b = b
		def __getstate__(self): return self.a, self.b
		def __setstate__(self, data): self.a, self.b = data
	test(ManySlotsTuple)

	class ManyElementDictTuple(object):
		def __init__(self, a, b): self.a = a; self.b = b; self.c = self.d = self.e = self.f = self.g = self.h = self.i = self.j = self.k = self.l = self.m = self.n = self.o = self.p = self.q = self.r = self.s = self.t = self.u = self.v = self.w = self.x = self.y = self.z = 0
		def __getstate__(self): return self.a, self.b
		def __setstate__(self, data): self.a, self.b = data
	test(ManyElementDictTuple)
