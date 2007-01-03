# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

_template = {}

def template(base):
	try: return _template[base]
	except KeyError:
	
		class result(base):
			def __init__(self, *args, **kw):
				base.__init__(self, *args, **kw)
				self._args = args
				self._kw = kw
				
			def check_and_build(self):
				try: return self._check_and_build
				except AttributeError:
					self._check_and_build = base(*self._args, **self._kw)
					self._check_and_build.attach(self)
					for attached in self._attached:
						if isinstance(attached, result): self._check_and_build.attach(attached.check_and_build())
					return self._check_and_build

			def build(self):
				try: return self._build
				except AttributeError:
					self._build = base(*self._args, **self._kw)
					self._build.attach(self.source())
					self._build.attach(self.check_and_build())
					for attached in self._attached:
						if isinstance(attached, result): self._build.attach(attached.build())
					return self._build

			def source(self):
				try: return self._source
				except AttributeError:
					self._source = base(*self._args, **self._kw)
					self._source.attach(self)
					for attached in self._attached:
						if isinstance(attached, result): self._source.attach(attached.source())
					return self._source

			class _client(base):
				def __init__(self, enclosing):
					base.__init__(self, *enclosing._args, **enclosing._kw)
					self._enclosing = enclosing
				
				def uninstalled(self):
					try: return self._uninstalled
					except AttributeError:
						self._uninstalled = base(*self._enclosing._args, **self._enclosing._kw)
						self._uninstalled.attach(self)
						self._uninstalled.attach(self._enclosing.source())
						for attached in self._attached:
							if isinstance(attached, result._client): self._uninstalled.attach(attached.uninstalled())
						return self._uninstalled
						
				def installed(self):
					try: return self._installed
					except AttributeError:
						self._installed = base(*self._enclosing._args, **self._enclosing._kw)
						self._installed.attach(self)
						for attached in self._attached:
							if isinstance(attached, result._client): self._installed.attach(attached.installed())
						return self._installed

				def attach(self, source):
					base.attach(self, source)
					if isinstance(source, result._client):
						try: uninstalled = self._uninstalled
						except AttributeError: pass
						else: uninstalled.attach(source.uninstalled())
						
						try: installed = self._installed
						except AttributeError: pass
						else: installed.attach(source.installed())

			def client(self):
				try: return self._client_
				except AttributeError:
					self._client_ = self._client(self)
					self._client_.attach(self)
					for attached in self._attached:
						if isinstance(attached, self._client): self._client_.attach(attached.client())
					return self._client_

			def attach(self, source):
				base.attach(self, source)
				if isinstance(source, result):
					try: check_and_build = self._check_and_build
					except AttributeError: pass
					else: check_and_build.attach(source.check_and_build())

					try: build = self._build
					except AttributeError: pass
					else: build.attach(source.build())
			
					try: source_ = self._source
					except AttributeError: pass
					else: source_.attach(source.source())

					try: client = self._client_
					except AttributeError: pass
					else: client.attach(source.client())
					
		_template[base] = result
		return result
