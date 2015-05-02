# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

from attachable import attachable

class value(attachable):
	def __init__(self, value = None):
		attachable.__init__(self)
		self._value = value
		self._cached = False
		self._cached_value = None
		self._children = []
		#self._parents = []
		self._parents = self._attached
	
	def get(self):
		if self._cached: return self._cached_value
		self._cached = True
		if self._value is not None:
			self._cached_value = self._value
			return self._cached_value
		for value in self._parents:
			value = value.get()
			if value is not None:
				self._cached_value = value
				return self._cached_value
		self._cached_value = None
		return self._cached_value
	
	def set(self, value):
		self._value = value
		self._reset_cache()
	
	def __str__(self): return str(self.get())
	
	def attach(self, value_):
		assert isinstance(value_, value)
		attachable.attach(self, value_)
		# handled by attachable class since self._parents is just an alias for self._attached: self._parents.append(value_)
		value_._children.append(self)
		if self._cached and self._cached_value is None:
			self._cached = False
			self._reset_children_cache()

	def _reset_cache(self):
		if self._cached:
			self._cached = False
			self._cached_value = None
			self._reset_children_cache()

	def _reset_children_cache(self):
		for child in self._children: child._reset_cache()
