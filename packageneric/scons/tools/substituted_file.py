# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

def exists(env):
	return True

def generate(env, **kw):
	"""
	Adds SubstitutedFile builder, which substitutes the keys->values of SUBSTITUTION_DICTIONARY from the source to the target.
	The values of SUBSTITUTION_DICTIONARY first have any construction variables expanded (its keys are not expanded).
	If a value of SUBSTITUTION_DICTIONARY is a python callable function, it is called and the result is expanded as the value.
	"""
	
	name = 'SubstitutedFile'
	dictionary_name = 'SUBSTITUTION_DICTIONARY'

	def do(target_file_name, source_file_name, dictionary):
		"""
		Replace all instances of the keys of dictionary with their values.
		For example, if dictionary is {'%VERSION%': '1.2345', '%BASE%': 'my_program'},
		then all instances of %VERSION% in the file will be replaced with 1.2345 etc.
		"""
		try:
			f = open(source_file_name, 'rb')
			try: contents = f.read()
			finally: f.close()
		except:
			import SCons.Errors
			raise SCons.Errors.UserError, 'packagneric: cannot read source file %s' % source_file_name
		for (k,v) in dictionary.items():
			import re
			contents = re.sub(k, v, contents)
		try:
			f = open(target_file_name, 'wb')
			try: f.write(contents)
			finally: f.close()
		except:
			import SCons.Errors
			raise SCons.Errors.UserError, 'packageneric: cannot write target file %s' % target_file_name
		return 0 # success

	def action(target, source, env):
		return do(str(target[0]), str(source[0]), env['_' + dictionary_name + '_EXPANDED'])

	def string(target, source, env):
		"""This is what gets printed on the console."""
		from packageneric.scons.tty_font import tty_font
		return tty_font(font = '33', text = 'packageneric: substituting ' + str(source[0]))

	def emitter(target, source, env):
		"""
		Add dependency from substituted SUBSTITUTION_DICTIONARY to target.
		Returns original target, source tuple unchanged.
		"""
		try: d = dict(env[dictionary_name]) # copy it
		except KeyError:
			import SCons.Errors
			raise SCons.Errors.UserError, 'packageneric: ' + name + ' requires ' + dictionary_name + ' to be set in environment.'
		for (k,v) in d.items():
			if callable(v): d[k] = env.subst(v())
			else:
				import SCons.Util
				if SCons.Util.is_String(v): d[k] = env.subst(v)
				else:
					import SCons.Errors
					raise SCons.Errors.UserError, 'packageneric: in environment dictionary ' + dictionary_name + ', key %s: %s must be a string or callable' % (k, repr(v))
		env['_' + dictionary_name + '_EXPANDED'] = d
		import SCons.Node.Python
		env.Depends(target, SCons.Node.Python.Value(d))
		return target, source

	import SCons.Builder, SCons.Action
	env['BUILDERS'][name] = SCons.Builder.Builder(action = SCons.Action.Action(action, string), emitter = emitter)
	if not env.has_key(dictionary_name): env[dictionary_name] = {}
