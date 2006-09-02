# http://www.scons.org/cgi-sys/cgiwrap/scons/moin.cgi/SubstInFileBuilder

import os.path
from SCons.Script import *  # the usual scons stuff you get in a SConscript

def exists(env):
	return True

def generate(env, **kw):
	"""Adds WriteToFile builder, which writes any SCons.Node.Python.Value node to a file."""
	env.Append(TOOLS = 'WRITE')

	def do_write_to_file(targetfile, contents):
		try:
			f = open(os.path.basename(targetfile), 'wb')
			f.write(contents)
			f.close()
		except:
			raise SCons.Errors.UserError, "Can't write target file %s"%targetfile
		return 0 # success

	def write_to_file(target, source, env):
		return do_write_to_file(str(target[0]), env)

	def write_to_file_string(target, source, env):
		"""This is what gets printed on the console."""
		return 'packageneric: writing to %s' % str(target[0])

	def write_emitter(target, source, env):
		"""Add dependency from SCons.Node.Python.Value node to target."""
		source = SCons.Node.Python.Value(source)
		Depends(target, source)
		return target, source

	write_action=SCons.Action.Action(write_to_file, write_to_file_string)
	env['BUILDERS']['WriteToFile'] = Builder(action=write_action, emitter=write_emitter)
