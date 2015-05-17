#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2013-2015 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>


##############################################################################
#
# this script tests the filesystem cache
#
##############################################################################

if __name__ == '__main__':
	try: import wonderbuild
	except ImportError:
		import sys, os
		dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
		if dir not in sys.path: sys.path.append(dir)
		try: import wonderbuild
		except ImportError:
			print >> sys.stderr, 'could not import wonderbuild module with path', sys.path
			sys.exit(1)
	
	import os, errno, cPickle, gc, time
	from wonderbuild.filesystem import FileSystem
	
	def load_persistent(file):
		gc_enabled = gc.isenabled()
		if gc_enabled:
			try: gc.disable()
			except NotImplementedError: pass # jython uses the gc of the jvm
		try:
			t0 = time.time()
			try:
				persistent = cPickle.load(file)
			except EOFError:
				print '\tpickle: new file'
				return {}
			print '\tpickle: load time: {:.2f} seconds'.format(time.time() - t0)
			return persistent
		finally:
			if gc_enabled: gc.enable()
	
	def dump_persistent(persistent, file):
			gc_enabled = gc.isenabled()
			if gc_enabled:
				try: gc.disable()
				except NotImplementedError: pass # jython uses the gc of the jvm
			try:
				tell0 = file.tell()
				t0 = time.time()
				cPickle.dump(persistent, file, cPickle.HIGHEST_PROTOCOL)
				print '\tpickle: dump time: {:.2f} seconds'.format(time.time() - t0)
				print '\tpickle: size: {:.2f} MiB'.format(((file.tell() - tell0) * 1000. / (1 << 20)) * .001)
			finally:
				if gc_enabled: gc.enable()
	
	def process(fs):
		files = []
		for x in (fs.root / 'usr' / 'src').find_iter(('*.cpp', '*.c', '*.hpp', '*.h')):
			files.append(x)
		for x in (fs.root / 'usr' / 'include').find_iter(('*.hpp', '*.h')):
			files.append(x)
		for x in (fs.root / 'usr' / 'lib').find_iter(('*.so', '*.so.*'), prune_pats=('private','llvm-*')): # perm denied and cycling symlinks
			files.append(x)
		return files

	def timed(call):
		gc.collect()
		t0 = time.time()
		files = call()
		t1 = time.time()
		print '{} files in {:6.2f} seconds: {:10.0f} f/s'.format(len(files), t1 - t0, len(files) / (t1 - t0))
		gc.collect()

	def process_without_pickle(fs):
		return process(fs)
	
	def process_with_pickle(file):
		persistent = load_persistent(file)
		fs = FileSystem(persistent)
		files = process(fs)
		fs.purge(global_purge=False)
		file.seek(0, 0)
		dump_persistent(persistent, file)
		file.truncate()
		return files
	
	fs = FileSystem({})
	for x in xrange(2):
		timed(lambda: process_without_pickle(fs))
	fs = None
	gc.collect()

	persistent_path = os.path.join(os.path.dirname(__file__), '++persitent.pickle')

	try: os.unlink(persistent_path)
	except OSError: pass

	for x in xrange(2):
		try: f = open(persistent_path, 'r+b')
		except IOError, e:
			if e.errno != errno.ENOENT: raise
			f = open(persistent_path, 'w+b')
		timed(lambda: process_with_pickle(f))
		f.flush()
		os.fsync(f)
		f.close()
	os.unlink(persistent_path)

