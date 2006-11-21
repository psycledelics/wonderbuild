# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006 johan boule <bohan@jabber.org>
# copyright 2006 psycledelics http://psycle.pastnotecut.org

_template = {}

def template(mixin):
	try: return _template[mixin]
	except KeyError:
		import compiler
		base = compiler.template(mixin)
		
		class result(base):
			def __init__(self, project,
				defines = None,
				*args, **kw
			):
				base.__init__(*(self, project) + args, **kw)
				if defines is not None: self.compiler().defines().add(defines)

			def defines(self):
				try: return self._defines
				except AttributeError:
					from dictionary import dictionary
					self._defines = dictionary()
					return self._defines
				
			def attach(self, source):
				base.attach(self, source)
				if isinstance(source, result):
					self.defines().attach(source.defines())
					
			def _scons(self, scons):
				base._scons(self, scons)
				
				value = self.static().command().get()
				if value is not None: scons['CXX'] = value

				value = self.static().message().get()
				if value is not None: scons['CXXCOMSTR'] = value

				value = self.shared().command().get()
				if value is not None: scons['SHCXX'] = value

				value = self.shared().message().get()
				if value is not None: scons['SHCXXCOMSTR'] = value
				
				scons.Append(
					CXXFLAGS = self.flags().get()
				)
				scons.AppendUnique(
					CPPPATH = self.paths().get(),
					CPPDEFINES = self.defines().get()
				)
					
		_template[mixin] = result
		return result
