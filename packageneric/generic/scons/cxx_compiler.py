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
				if defines is not None: self.defines().add(defines)

			from dictionary import dictionary
			class _defines(dictionary):
				def substituted_files(self):
					try: return self._substituted_files
					except AttributeError:
						self._substituted_files = []
						return self._substituted_files

				def substituted_file(self, target, source):
					self.substituted_files().append([target, source])

				def _scons(self, scons):
					defines = self.get()
					scons.Append(CPPDEFINES = defines)
					for target, source in self.substituted_files():
						# scons.SubstitutedFile(target, source, defines)
						pass
						
			def defines(self):
				try: return self._defines_
				except AttributeError:
					self._defines_ = result._defines()
					return self._defines_
				
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
				
				scons.Append(CXXFLAGS = self.flags().get())
				scons.AppendUnique(CPPPATH = self.paths().get())
				self.defines()._scons(scons)
					
		_template[mixin] = result
		return result
