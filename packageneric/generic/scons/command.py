# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

_template = {}

def template(base):
	try: return _template[base]
	except KeyError:

		class result(base):
			def __init__(self, project,
				command = None,
				message = None,
				*args, **kw
			):
				base.__init__(*(self, project) + args, **kw)
				if command is not None: self.command().set(command)
				if message is not None: self.message().set(message)

			def command(self):
				try: return self._command
				except AttributeError:
					from value import value
					self._command = value()
					return self._command
			
			def message(self):
				try: return self._message
				except AttributeError:
					from value import value
					self._message = value()
					return self._message
			
			def attach(self, source):
				base.attach(self, source)
				if isinstance(source, result):
					self.command().attach(source.command())
					self.message().attach(source.message())

		_template[base] = result
		return result
