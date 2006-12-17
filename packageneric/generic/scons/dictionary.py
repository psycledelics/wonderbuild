# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006 johan boule <bohan@jabber.org>
# copyright 2006 psycledelics http://psycle.pastnotecut.org

from set import set

class dictionary(set):
	def __init__(self, dictionary_ = None):
		if dictionary_ is None: dictionary_ = {}
		set.__init__(self, dictionary_)
	
	def get(self):
		if self._cached: return self._cached_value
		values = []
		values.extend(self._parents)
		values.reverse()
		result = {}
		for value in [value_.get() for value_ in values]: result.update(value)
		result.update(self._value)
		self._cached = True
		self._cached_value = result
		return self._cached_value
	
	def __setitem__(self, key, value):
		self._value[key] = value
		self._reset_cache()

	def add_unique(self, dictionary_):
		self._value.update(dictionary_)
		self._reset_cache()
