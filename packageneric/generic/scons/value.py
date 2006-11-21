# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006 johan boule <bohan@jabber.org>
# copyright 2006 psycledelics http://psycle.pastnotecut.org

from attachable import attachable

class value(attachable):
	def __init__(self, value = None):
		self._value = value
		self._values = []
	
	def get(self):
		if self._value is not None: return self._value
		for value in self._values:
			value = value.get()
			if value is not None: return value
		return None
	
	def set(self, value): self._value = value
	
	def __str__(self): return str(self.get())
	
	def attach(self, value_):
		attachable.attach(self, value_)
		assert isinstance(value_, value)
		self._values.append(value_)
