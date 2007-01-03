# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

from list import list

class set(list):
	def add(self, x): self.add_unique(x)

	def get(self):
		if self._cached: return self._cached_value
		if True:
			result = self._value[:]
			for values in [value_.get() for value_ in self._parents]: result.extend(values)
			from SCons.Util import unique
			self._cached_value = unique(result)
			self._cached = True
			return self._cached_value
		else:
			result = self._value[:]
			for values in [value_.get() for value_ in self._parents]:
				for value in values:
					if value not in result: result.append(value)
			self._cached = True
			self._cached_value = result
			return self._cached_value
