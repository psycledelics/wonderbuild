# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

_template = {}

def template(base): # attachable
	try: return _template[base]
	except KeyError:
		
		class result(base):
			def command(self): return self.static().command()
			
			def static(self):
				try: return self._static
				except AttributeError:
					import command
					from attachable import attachable
					self._static = command.template(attachable)(self.project())
					return self._static

			def shared(self):
				try: return self._shared
				except AttributeError:
					import command
					from attachable import attachable
					self._shared = command.template(attachable)(self.project())
					return self._shared
				
			def attach(self, source):
				base.attach(self, source)
				if isinstance(source, result):
					self.static().attach(source.static())
					self.shared().attach(source.shared())

		_template[base] = result
		return result
