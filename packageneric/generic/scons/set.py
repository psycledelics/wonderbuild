# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006 johan boule <bohan@jabber.org>
# copyright 2006 psycledelics http://psycle.pastnotecut.org

from list import list

class set(list):
	def add(self, x): self.add_unique(x)

	def get(self):
		if self._cached: return self._cached_value
		result = []
		result.extend(self._value)
		for values in [value_.get() for value_ in self._parents]:
			for value in values:
				if value not in result: result.append(value)
		self._cached = True
		self._cached_value = result
		return self._cached_value
