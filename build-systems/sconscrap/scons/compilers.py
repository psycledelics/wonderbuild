# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

class compilers:
	def __init__(self, compilers = None):
		if compilers is not None: self._compilers = compilers
		else: self._compilers = []
		
	def add(self, name, compiler):
		self._compilers.append(compiler)
		setattr(self, name, lambda: compiler)
		
	def __getitem__(self, index): return self._compilers[index]
