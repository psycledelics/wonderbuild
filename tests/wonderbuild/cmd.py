#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

class Cmd:
	def args(self): pass
	def message(self): pass

	def run(self): return exec_subprocess(self.args())

import sys, subprocess

def exec_subprocess(args): return exec_subprocess_3(args)

def exec_subprocess_1(args): # not sure
	p = subprocess.Popen(
		args = args,
		stdout = subprocess.PIPE,
		stderr = subprocess.PIPE,
		bufsize = 0,
		shell = False,
		env = {}
	)
	out_eof = err_eof = False
	while not(out_eof and err_eof):
		if not out_eof:
			r = p.stdout.read()
			if not r: out_eof = True
			else: sys.stdout.write(r)
		if not err_eof:
			r = p.stderr.read()
			if not r: err_eof = True
			else: sys.stderr.write(r)
	return p.wait()

def exec_subprocess_2(args): # broken! doesn't not wait for completion!
	p = subprocess.Popen(
		args = args,
		stdout = subprocess.PIPE,
		stderr = subprocess.PIPE,
		bufsize = 0,
		shell = False,
		env = {}
	)
	while p.poll() is None:
		r = p.stdout.readline()
		if len(r) != 0: sys.stdout.write(r)
		r = p.stderr.readline()
		if len(r) != 0: sys.stderr.write(r)
	return p.returncode

def exec_subprocess_3(args): # ok
	p = subprocess.Popen(
		args = args,
		stdout = subprocess.PIPE,
		stderr = subprocess.PIPE,
		bufsize = 0,
		shell = False,
		env = {}
	)
	out, err = p.communicate()
	sys.stdout.write(out)
	sys.stderr.write(err)
	return p.returncode

if __name__ == '__main__':
	if len(sys.argv) < 2:
		sys.stderr.write('usage: ' + sys.argv[0] + ' <cmd> <args>\n')
		sys.exit(1)
	args = sys.argv[1:]
	print 'args:', args
	print 'return code: ' + str(exec_subprocess(args))

