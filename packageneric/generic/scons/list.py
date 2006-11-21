# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006 johan boule <bohan@jabber.org>
# copyright 2006 psycledelics http://psycle.pastnotecut.org

from value import value

class list(value):
	def __init__(self, list_ = None):
		if list_ is None: list_ = []
		value.__init__(self, list_)
		
	def get(self):
		result = []
		result.extend(self._value)
		for value in [value.get() for value in self._values]: result.extend(value)
		return result

	def __len__(self):
		result = len(self._value)
		for value in self._values: result += len(value)
		return result
	
	def __getitem__(self, index):
		try: return self._value[index]
		except IndexError:
			index -= len(self._value)
			for value in self._values:
				try: return value[index]
				except IndexError: index -= len(value)
			return self._value[index] # raises the original IndexError

	def add(self, list_): self._value.extend(list_)
	
	def add_unique(self, list_):
		for value in list_:
			if not value in self: self._value.append(value)
			
	def __contains__(self, element):
		if element in self._value: return True
		for value in self._values:
			if element in value: return True
		return False
		if False:
			# the following alternative implementation is much more slower
			for x in self:
				if x == element: return True
			return False

			# even more slower
			for x in self:
				if x is element: return True
			return False
