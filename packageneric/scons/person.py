# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

class person:
	def __init__(
		self,
		name,
		email
	):
		self._name = name
		self._email = email
		
	def name(self):
		return self._name
	
	def email(self):
		return self._email
