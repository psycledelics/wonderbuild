# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006 johan boule <bohan@jabber.org>
# copyright 2006 psycledelics http://psycle.pastnotecut.org

from set import set

class dictionary(set):
	def __init__(self, dictionary_ = None):
		if dictionary_ is None: dictionary_ = {}
		set.__init__(self, dictionary_)
	
	def get(self):
		values = []
		values.extend(self._values)
		values.reverse()
		result = {}
		for value in [value.get() for value in values]: result.update(value)
		result.update(self._value)
		return result
	
	def __getitem__(self, key):
		try: return self._value[key]
		except KeyError:
			for value in self._values:
				try: return value[key]
				except KeyError: pass
			return self._value[key] # raises the original KeyError

	def __setitem__(self, key, value): self._value[key] = value

	def add_unique(self, dictionary_): self._value.update(dictionary_)
