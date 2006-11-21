# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006 johan boule <bohan@jabber.org>
# copyright 2006 psycledelics http://psycle.pastnotecut.org

class attachable:
	def __init__(self, *args, **kw): pass
	
	def attach(self, source): assert isinstance(source, attachable)

	def attached(self, *args, **kw):
		result = self.__class__(*args, **kw)
		result.attach(self)
		return result
