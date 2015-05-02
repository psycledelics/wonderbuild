# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

def exists(env):
	return True

def generate(env, **kw):
	def do(file_name, contents):
		try:
			f = open(file_name, 'wb')
			try: f.write(contents)
			finally: f.close()
		except:
			import SCons.Errors
			raise SCons.Errors.UserError, 'packageneric: cannot write to target file %s' % file_name
		return 0 # success

	def action(target, source, env): return do(str(target[0]), source[0].get_contents())

	def string(target, source, env):
		"""This is what gets printed on the console."""
		from packageneric.scons.tty_font import tty_font
		return tty_font(font = '32', text = 'packageneric: writing ' + str(target[0]))

	import SCons.Builder, SCons.Action
	env['BUILDERS']['FileFromValueBuilder'] = SCons.Builder.Builder(action = SCons.Action.Action(action, string))

	def invoke(file_name, contents, env = env):
		import SCons.Node.Python
		if not isinstance(contents, SCons.Node.Python.Value): contents = SCons.Node.Python.Value(contents)
		return env.FileFromValueBuilder(file_name, contents)

	env.FileFromValue = invoke
