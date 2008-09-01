# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

_template = {}

def template(mixin):
	try: return _template[mixin]
	except KeyError:
		import command, flags
		base = \
			command.template(
			flags.template(
			mixin))
		
		class result(base):
			def __init__(self, project,
				*args, **kw
			):
				base.__init__(*(self, project) + args, **kw)

			def indexer(self):
				try: return self._indexer
				except AttributeError:
					import archive_indexer as indexer
					self._indexer = indexer.template(base)(self.project())
					return self._indexer
				
			def attach(self, source):
				base.attach(self, source)
				if isinstance(source, result): self.indexer().attach(source.indexer())
				
			def _scons(self, scons):
				base._scons(self, scons)
				self.indexer()._scons(scons)

				value = self.command().get()
				if value is not None: scons['AR'] = value

				value = self.message().get()
				if value is not None: scons['ARCOMSTR'] = value

				scons.Append(
					ARFLAGS = self.flags().get()
				)

		_template[mixin] = result
		return result
