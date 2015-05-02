# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

from value import value

class list(value):
	def __init__(self, list_ = None):
		if list_ is None: list_ = []
		value.__init__(self, list_)
		self._cached_flat_unique_parents = None
		
	def get(self):
		if self._cached: return self._cached_value
		result = self._value[:]
		for value in [value_._value for value_ in self._flat_unique_parents()]: result.extend(value)
		self._cached = True
		self._cached_value = result
		return self._cached_value

	def __len__(self): return len(self.get())
	
	def __getitem__(self, index): return self.get().__getitem__(index)

	def add(self, list_):
		self._value.extend(list_)
		if self._cached:
			self._cached_value.extend(list_)
			self._reset_children_cache()
	
	def add_unique(self, list_):
		need_cache_reset = False
		for value in list_:
			if value not in self:
				self._value.append(value)
				if self._cached:
					self._cached_value.append(value)
					need_cache_reset = True
		if need_cache_reset: self._reset_children_cache()
			
	def __contains__(self, element): return element in self.get()

	def attach(self, list_):
		assert isinstance(list_, list)
		value.attach(self, list_)
		if self._cached:
			if self._cached_flat_unique_parents is None: self._reset_cache()
			elif list_ not in self._cached_flat_unique_parents:
				self._cached_flat_unique_parents.append(list_)
				self._reset_cache()

	def _flat_unique_parents(self):
		if self._cached_flat_unique_parents is not None: return self._cached_flat_unique_parents
		result = self._parents[:]
		for parent in self._parents: result.extend(parent._flat_unique_parents())
		from SCons.Util import unique
		self._cached_flat_unique_parents = unique(result)
		return self._cached_flat_unique_parents
