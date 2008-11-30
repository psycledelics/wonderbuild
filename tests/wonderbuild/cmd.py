#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import sys, os, subprocess

class Cmd(object):
	def __init__(self, args, message = None):
		self.args = args
		self.message = message

	def run(self):
		print self.message or self.args
		if self.args is None: return 0
		return exec_subprocess(self.args)

def exec_subprocess(args, env = os.environ, out_stream = sys.stdout, err_stream = sys.stderr):
	print args
	p = subprocess.Popen(
		args = args,
		stdout = subprocess.PIPE,
		stderr = subprocess.PIPE,
		bufsize = 0,
		shell = False,
		env = env
	)
	out, err = p.communicate()
	out_stream.write(out)
	err_stream.write(err)
	return p.returncode

if __name__ == '__main__':
	if len(sys.argv) < 2:
		sys.stderr.write('usage: ' + sys.argv[0] + ' <cmd> <args>\n')
		sys.exit(1)
	cmd = Cmd(sys.argv[1:])
	r = cmd.run()
	print 'return code: ' + str(r)
