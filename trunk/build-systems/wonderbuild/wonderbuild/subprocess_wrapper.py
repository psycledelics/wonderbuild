#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import sys, subprocess, threading
from logger import out, is_debug, debug, colored

#########################################
# OptionDecl

known_options = set(['sync-log', 'make-like-messages'])

def generate_option_help(help):
	help['sync-log'] = ('[yes|no]', 'synchronize concurrent log outputs (std out and err)', 'no')
	help['make-like-messages'] = ('[yes|no]', 'output messages like the make build tool when executing subprocess command lines', 'no')

#########################################
# use_options(options)
# which defines:
# - sync_log
# - make_like_messages
# - def out(s)
# - def err(s)

sync_log = False
make_like_messages = False
def use_options(options):
	global sync_log
	sync_log = options.get('sync-log', 'no') != 'no'

	global make_like_messages
	make_like_messages = options.get('make-like-messages', 'no') != 'no'

#########################################

#out = sys.stdout logger.out
err = sys.stderr

#########################################

if __debug__ and is_debug:
	import os
	def _env_diff(env):
		env_diff = {}
		if env is not None:
			for k, v in env.iteritems():
				try: vv = os.environ[k]
				except KeyError: env_diff[k] = v
				else:
					if v != vv: env_diff[k] = v
		return env_diff

def exec_subprocess(args, env=None, cwd=None):
	if __debug__ and is_debug:
		debug('exec: ' + str(cwd) + ' ' + str(_env_diff(env)) + ' ' + str(args))
	do_msg = cwd is not None and make_like_messages
	if do_msg: out.write('make: Entering directory `' + cwd + "'\n")
	if make_like_messages: out.write(' '.join(args) + '\n')
	r = subprocess.call(args=args, bufsize=-1, env=env, cwd=cwd)
	if do_msg: out.write('make: Leaving directory `' + cwd + "'\n")
	return r

if False:
	_stdouterr_lock = threading.Lock()
	_stdouterr_flag_lock = threading.Lock()
	_stdouterr_locked = False
	old_exec_subprocess = exec_subprocess
	def exec_subprocess(args, env = None, cwd = None):
		_stdouterr_flag_lock.acquire()
		try:
			global _stdouterr_locked
			silent = _stdouterr_locked
			if not silent: _stdouterr_locked = True
		finally: _stdouterr_flag_lock.release()
		try:
			if not silent:
				r = old_exec_subprocess(args=args, env=env, cwd=cwd)
			else:
				r, stdout, stderr = exec_subprocess_pipe(args, input=None, env=env, cwd=cwd, silent=True)
				_stdouterr_lock.acquire()
				try:
					out.write(stdout)
					err.write(stderr)
				finally: _stdouterr_lock.release()
			return r
		finally:
			if not silent:
				_stdouterr_flag_lock.acquire()
				try: _stdouterr_locked = False
				finally: _stdouterr_flag_lock.release()

_fork_lock = threading.Lock() # workaround for bug still present in python 2.5.2, used in exec_subprocess_pipe

def exec_subprocess_pipe(args, input=None, env=None, cwd=None, silent=False):
	if __debug__ and is_debug: debug('exec: pipe: ' + str(cwd) + ' ' + str(_env_diff(env)) + ' ' + str(args))
	if input is not None:
		_fork_lock.acquire() # workaround for bug still present in python 2.5.2
		try: p = subprocess.Popen(args=args, bufsize=-1, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, cwd=cwd)
		finally: _fork_lock.release()
	else: p = subprocess.Popen(args=args, bufsize=-1, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, cwd=cwd)
	if input is not None:
		if __debug__ and is_debug:
			for line in input.split('\n')[:-1]: debug('exec: pipe: ' + colored('7;36', 'in') + ': ' + line)
		elif not silent:
			out.write('\n')
			out.write(input)
	stdout, stderr = p.communicate(input)
	if __debug__ and is_debug:
		if len(stdout):
			for line in stdout.split('\n')[:-1]: debug('exec: pipe: ' + colored('7;32', 'out') + ': ' + line)
		if len(stderr):
			s = ''
			for line in stderr.split('\n')[:-1]: debug('exec: pipe: ' + colored('7;1;31', 'err') + ': ' + line)
			debug(s)
		if p.returncode == 0: debug('exec: pipe: ' + colored('7;32', 'ret') + ': ' + str(p.returncode) + ' ok')
		else: debug('exec: pipe: ' + colored('7;1;31', 'ret') + ': ' + str(p.returncode) + ' failed')
	elif not silent:
		if len(stdout):
			s = ''
			for line in stdout.split('\n')[:-1]: s += 'exec: pipe: ' + colored('7;32', 'out') + ': ' + line + '\n'
			out.write(s)
		if len(stderr):
			s = ''
			for line in stderr.split('\n')[:-1]: s += 'exec: pipe: ' + colored('7;31', 'err') + ': ' + line + '\n'
			err.write(s)
		if p.returncode == 0: out.write('exec: pipe: ' + colored('7;32', 'ret') + ': ' + str(p.returncode) + ' ok\n')
		else: err.write('exec: pipe: ' + colored('7;1;31', 'ret') + ': ' + str(p.returncode) + ' failed\n')
	return p.returncode, stdout, stderr
