# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006 johan boule <bohan@jabber.org>
# copyright 2006 psycledelics http://psycle.pastnotecut.org

_template = {}

def template(mixin):
	try: return _template[mixin]
	except KeyError:
		import chain
		base = chain.template(mixin)

		class result(base):
			def __init__(self, project,
				cxx_compiler_defines = None,
				cxx_compiler_paths = None,
				cxx_compiler_flags = None,
				*args, **kw
			):
				base.__init__(*(self, project) + args, **kw)
				import cxx_compiler
				self.compilers().add('cxx', cxx_compiler.template(base)(project, *args, **kw))
				if cxx_compiler_defines is not None: self.compilers().cxx().defines().add(cxx_compiler_defines)
				if cxx_compiler_paths is not None: self.compilers().cxx().paths().add(cxx_compiler_paths)
				if cxx_compiler_flags is not None: self.compilers().cxx().flags().add(cxx_compiler_flags)
				
		_template[mixin] = result
		return result
