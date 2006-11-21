# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006 johan boule <bohan@jabber.org>
# copyright 2006 psycledelics http://psycle.pastnotecut.org

from list import list

class set(list):
	def add(self, x): self.add_unique(x)

	if False:
		def add_unique(self, list_):
			for value in list_: self._value.append(value)

		def get(self):
			result = []
			for value in self:
				if value not in result: result.append(value)
			return result
