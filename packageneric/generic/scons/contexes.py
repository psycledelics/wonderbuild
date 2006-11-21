# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006 johan boule <bohan@jabber.org>
# copyright 2006 psycledelics http://psycle.pastnotecut.org

_template = {}

def template(base):
	try: return _template[base]
	except KeyError:
	
		class result(base):
			def __init__(self, *args, **kw):
				base.__init__(self, *args, **kw)
				self._args = args
				self._kw = kw
				
			def build(self):
				try: return self._build
				except AttributeError:
					self._build = base(*self._args, **self._kw)
					self._build.attach(self)
					return self._build

			class _client(base):
				def __init__(self, enclosing):
					base.__init__(self, *enclosing._args, **enclosing._kw)
					self._enclosing = enclosing
				
				def uninstalled(self):
					try: return self._uninstalled
					except AttributeError:
						self._uninstalled = base(*self._enclosing._args, **self._enclosing._kw)
						self._uninstalled.attach(self)
						return self._uninstalled
						
				def installed(self):
					try: return self._installed
					except AttributeError:
						self._installed = base(*self._enclosing._args, **self._enclosing._kw)
						self._installed.attach(self)
						return self._installed

				def attach(self, source):
					base.attach(self, source)
					if isinstance(source, result._client):
						self.uninstalled().attach(source.uninstalled())
						self.installed().attach(source.installed())

			def client(self):
				try: return self._client_
				except AttributeError:
					self._client_ = result._client(self)
					self._client_.attach(self)
					return self._client_

			def attach(self, source):
				base.attach(self, source)
				if isinstance(source, result):
					self.build().attach(source.build())
					self.client().attach(source.client())
			
		_template[base] = result
		return result
