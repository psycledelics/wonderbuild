# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

_template = {}

def template(mixin):
	try: return _template[mixin]
	except KeyError:
		import compiler
		base = compiler.template(mixin)
		
		class result(base):
			def __init__(self, project,
				libraries = None,
				*args, **kw
			):
				base.__init__(*(self, project) + args, **kw)
				if libraries is not None: self.libraries().add(libraries)

			def loadable(self):
				try: return self._loadable
				except AttributeError:
					import command
					from attachable import attachable
					self._loadable = command.template(attachable)(self.project())
					return self._loadable
				
			def libraries(self):
				try: return self._libraries
				except AttributeError:
					from set import set
					self._libraries = set()
					return self._libraries
				
			def attach(self, source):
				base.attach(self, source)
				if isinstance(source, result):
					self.loadable().attach(source.loadable())
					self.libraries().attach(source.libraries())
					
			def _scons(self, scons):
				base._scons(self, scons)

				value = self.static().command().get()
				if value is not None: scons['LINK'] = value

				value = self.static().message().get()
				if value is not None: scons['LINKCOMSTR'] = value

				value = self.shared().command().get()
				if value is not None: scons['SHLINK'] = value

				value = self.shared().message().get()
				if value is not None: scons['SHLINKCOMSTR'] = value

				value = self.loadable().command().get()
				if value is not None: scons['LDMODULE'] = value

				value = self.loadable().message().get()
				if value is not None: scons['LDMODULECOMSTR'] = value

				scons.Append(
					LINKFLAGS = self.flags().get()
				)
				scons.AppendUnique(
					LIBPATH = self.paths().get(),
					LIBS = self.libraries().get()
				)

		_template[mixin] = result
		return result
