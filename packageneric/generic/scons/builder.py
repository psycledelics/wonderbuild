# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

from named import named

class builder(named):
	def __init__(self, name): named.__init__(self, name)
	def alias_names(self): raise self
	def targets(self): raise self
