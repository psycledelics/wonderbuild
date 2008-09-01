# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

#from list import list as base
from set import set as base

class flags_list(base):
	def add(self, flags):
		if flags is None: return
		string_flags = []
		for flag in flags:
			if len(flag) > 1: string_flags.append(flag)
			elif not len(self): base.add([flag])
			elif not flag in self[0]: self[0] += flag
		base.add(self, string_flags)

_template = {}

def template(base):
	try: return _template[base]
	except KeyError:

		class result(base):
			def __init__(self, project,
				flags = None,
				*args, **kw
			):
				base.__init__(*(self, project) + args, **kw)
				if not flags is None: self.flags().add(flags)

			def flags(self):
				try: return self._flags
				except AttributeError:
					self._flags = flags_list()
					return self._flags

			def attach(self, source):
				base.attach(self, source)
				if isinstance(source, result): self.flags().attach(source.flags())

		_template[base] = result
		return result
