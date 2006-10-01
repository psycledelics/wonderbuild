# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006 johan boule <bohan@jabber.org>
# copyright 2006 psycledelics http://psycle.pastnotecut.org

def exists(env):
	return True

def generate(env, **kw):
	"""
	Adds SubstInFile builder, which substitutes the keys->values of SUBST_DICT
	from the source to the target.
	The values of SUBST_DICT first have any construction variables expanded
	(its keys are not expanded).
	If a value of SUBST_DICT is a python callable function, it is called and
	the result is expanded as the value.
	If there's more than one source and more than one target, each target gets
	substituted from the corresponding source.
	"""
	
	name = 'SubstInFile'
	dictionary_name = 'SUBST_DICT'

	def do(target_file_name, source_file_name, dictionary):
		"""
		Replace all instances of the keys of dictionary with their values.
		For example, if dict is {'%VERSION%': '1.2345', '%BASE%': 'MyProg'},
		then all instances of %VERSION% in the file will be replaced with 1.2345 etc.
		"""
		try:
			f = open(source_file_name, 'rb')
			contents = f.read()
			f.close()
		except:
			import SCons.Errors
			raise SCons.Errors.UserError, 'packagneric: cannot read source file %s' % source_file_name
		for (k,v) in dictionary.items():
			import re
			contents = re.sub(k, v, contents)
		try:
			f = open(target_file_name, 'wb')
			f.write(contents)
			f.close()
		except:
			import SCons.Errors
			raise SCons.Errors.UserError, 'packageneric: cannot write target file %s' % target_file_name
		return 0 # success

	def action(target, source, env):
		return do(str(target[0]), str(source[0]), env['_' + dictionary_name + '_EXPANDED'])

	def string(target, source, env):
		"""This is what gets printed on the console."""
		return '\n'.join(['packageneric: substituting vars from %s into %s'%(str(s), str(t)) for (t,s) in zip(target, source)])

	def emitter(target, source, env):
		"""
		Add dependency from substituted SUBST_DICT to target.
		Returns original target, source tuple unchanged.
		"""
		if not env.has_key(dictionary_name):
			import SCons.Errors
			raise SCons.Errors.UserError, 'packageneric: ' + name + ' requires ' + dictionary_name + ' to be set in environment.'
		d = dict(env[dictionary_name]) # copy it
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
