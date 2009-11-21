#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import sys, subprocess

from logger import out, is_debug, debug, colored

known_options = set(['eclipse-cdt-discovery'])

def generate_option_help(help):
	help['eclipse-cdt-discovery'] = (None, 'output subprocess command lines in a way suitable for the eclipse cdt discovery to scan them')

eclipse_cdt_discovery = False
def use_options(options):
	global eclipse_cdt_discovery
	eclipse_cdt_discovery = 'eclipse-cdt-discovery' in options

def exec_subprocess(args, env = None, cwd = None):
	if __debug__ and is_debug: debug('exec: ' + str(cwd) + ' ' + str(env) + ' ' + str(args))
	if eclipse_cdt_discovery: print >> sys.stdout, 'make: Entering directory `' + str(cwd) + "'\n" + ' '.join(args)
	return subprocess.call(
		args = args,
		bufsize = -1,
		env = env,
		cwd = cwd
	)

def exec_subprocess_pipe(args, input = None, env = None, cwd = None, silent = False):
	if __debug__ and is_debug: debug('exec: pipe: ' + str(cwd) + ' ' + str(env) + ' ' + str(args))
	if input is not None:
		_lock.acquire() # workaround for bug still present in python 2.5.2
		try: p = subprocess.Popen(
				args = args,
				bufsize = -1,
				stdin = subprocess.PIPE,
				stdout = subprocess.PIPE,
				stderr = subprocess.PIPE,
				env = env,
				cwd = cwd
			)
		finally: _lock.release()
	else: p = subprocess.Popen(
			args = args,
			bufsize = -1,
			stdin = None,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			env = env,
			cwd = cwd
		)
	if input is not None:
		if __debug__ and is_debug:
			for line in input.split('\n')[:-1]: debug('exec: pipe: ' + colored('7;36', 'in') + ': ' + line)
		elif not silent:
			sys.stdout.write('\n')
			sys.stdout.write(input)
	out, err = p.communicate(input)
	if __debug__ and is_debug:
		if len(out):
			for line in out.split('\n')[:-1]: debug('exec: pipe: ' + colored('7;32', 'out') + ': ' + line)
		if len(err):
			s = ''
			for line in err.split('\n')[:-1]: debug('exec: pipe: ' + colored('7;1;31', 'err') + ': ' + line)
			debug(s)
		if p.returncode == 0: debug('exec: pipe: ' + colored('7;32', 'ret') + ': ' + str(p.returncode) + ' ok')
		else: debug('exec: pipe: ' + colored('7;1;31', 'ret') + ': ' + str(p.returncode) + ' failed')
	elif not silent:
		if len(out):
			s = ''
			for line in out.split('\n')[:-1]: s += 'exec: pipe: ' + colored('7;32', 'out') + ': ' + line + '\n'
			sys.stdout.write(s)
		if len(err):
			s = ''
			for line in err.split('\n')[:-1]: s += 'exec: pipe: ' + colored('7;31', 'err') + ': ' + line + '\n'
			sys.stderr.write(s)
		if p.returncode == 0: sys.stdout.write('exec: pipe: ' + colored('7;32', 'ret') + ': ' + str(p.returncode) + ' ok\n')
		else: sys.stderr.write('exec: pipe: ' + colored('7;1;31', 'ret') + ': ' + str(p.returncode) + ' failed\n')
	return p.returncode, out, err
# workaround for bug still present in python 2.5.2
import threading
_lock = threading.Lock() # used in exec_subprocess_pipe
