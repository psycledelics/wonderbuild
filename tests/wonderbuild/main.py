#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

if False and __name__ == '__main__':
	fs = FS(src = '.', bld = './++build')

	tm = TaskMaster()
	tm.start()

	i = fs.file('src/foo.hpp.in')
	o = fs.file('++build/src/foo.hpp')
	d = Dependency(o, Dependency.CONTENT, i)
	tm.add_dep(d)
	t = Task([i], ['cp -L', i.path(), o.path()], [o])
	tm.add_task(t)

	for i in fs.find('src', include_pattern = '*.cpp'):
		#i = fs.file('src/foo.cpp')
		o = fs.file(fs.ch_ext(fs.twin_path(i), '.cpp', '.o'))
		d = Dependency(o, Dependency.CONTENT, i)
		tm.add_dep(d)
		t = Task([i], ['c++', '-c', i.path(), '-o', o.path()], [o])
		tm.add_task(t)

	s = Scanner()
	s.append_path('src')
	s.append_path('++build/src')

	i = FileFSNode('src/foo.cpp')
	d = s.deps([i])
	ii = [i] + d
	o = FileFSNode('++build/src/foo.o')
	t = Task(ii, ['c++', '-c', i.path(), '-o', o.path()], [o])
	tm.add_task(t)

	i = FileFSNode('++build/src/foo.o')
	o = FileFSNode('++build/libfoo.so')
	t = Task([i], ['c++', '-shared', i.path(), '-o', o.path()], [o])
	tm.add_task(t)

	tm.end()
