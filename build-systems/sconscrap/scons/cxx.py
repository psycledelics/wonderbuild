# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

_template = {}

def template(base): # chain
	try: return _template[base]
	except KeyError:
		
		class result(base):
			def __init__(self, project,
				cxx_compiler_defines = None,
				cxx_compiler_paths = None,
				cxx_compiler_flags = None,
				*args, **kw
			):
				base.__init__(*(self, project) + args, **kw)
				import cxx_compiler
				self.compilers().add('cxx', cxx_compiler.template(self.env_class())(project))
				if cxx_compiler_defines is not None: self.compilers().cxx().defines().add(cxx_compiler_defines)
				if cxx_compiler_paths is not None: self.compilers().cxx().paths().add(cxx_compiler_paths)
				if cxx_compiler_flags is not None: self.compilers().cxx().flags().add(cxx_compiler_flags)
				
			def detect_implementation(self):
				import gnu
				if gnu.detect(self): self._implementation().set(lambda self: gnu.implementation(self))
				else:
					import msvc
					if msvc.detect(self): self._implementation().set(lambda self: msvc.implementation(self))

		_template[base] = result
		return result
