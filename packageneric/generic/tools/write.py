# http://www.scons.org/cgi-sys/cgiwrap/scons/moin.cgi/SubstInFileBuilder

from SCons.Script import *  # the usual scons stuff you get in a SConscript

def exists(env):
	return True

def generate(env, **kw):
	env.Append(TOOLS = 'WRITE')

	def do_write_to_file(file_name, contents):
		try:
			f = open(file_name, 'wb')
			f.write(contents)
			f.close()
		except:
			raise SCons.Errors.UserError, "Can't write target file %s" % file_name
		return 0 # success

	def write_to_file_command(env, target, source):
		return do_write_to_file(target[0].path, source[0].get_contents())

	def write_to_file_action(target, source, env):
		return do_write_to_file(target[0].path, source[0].get_contents())

	def write_to_file_string(target, source, env):
		return 'packageneric: writing to %s' % str(target[0])

	def write_emitter(target, source, env):
		source = SCons.Node.Python.Value(source)
		Depends(target, source)
		return target, source

	#env['BUILDERS']['WriteToFile'] = Builder(action=SCons.Action.Action(write_to_file_action, write_to_file_string), emitter=write_emitter)
	env.WriteToFile = lambda target, contents: Command(target, Value(contents), write_to_file_command)
