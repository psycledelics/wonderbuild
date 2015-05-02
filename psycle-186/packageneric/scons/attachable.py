# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

class attachable:
	def __init__(self, *args, **kw):
		self._attached = []

	def attach(self, source):
		assert isinstance(source, attachable)
		#assert source.assert_no_cycle(self)
		self._attached.append(source)

	def attached(self, *args, **kw):
		result = self.__class__(*args, **kw)
		result.attach(self)
		return result

	def assert_no_cycle(self, initial):
		assert initial not in self._attached
		for attached in self._attached: assert attached.assert_no_cycle(initial)
		return True
