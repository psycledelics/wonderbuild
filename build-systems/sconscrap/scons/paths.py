# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

_template = {}

def template(base):
	from attachable import attachable
	assert issubclass(base, attachable)
	try: return _template[base]
	except KeyError:

		class result(base):
			def __init__(self, project,
				paths = None,
				*args, **kw
			):
				base.__init__(*(self, project) + args, **kw)
				if paths is not None: self.paths().add(paths)

			def paths(self):
				try: return self._paths
				except AttributeError:
					from set import set
					self._paths = set()
					return self._paths

			def attach(self, source):
				base.attach(self, source)
				if isinstance(source, result): self.paths().attach(source.paths())
				
		_template[base] = result
		return result
