import os
from packages import Package

def package(packages): return ZLib(packages)

class ZLib(Package):
	def __init__(self, packages):
		Package.__init__(self, packages, 'zlib', '1.2.3')
		self.add_dep('gcc')

	def download(self): self.http_get(self.mirror('sourceforge') + '/libpng/zlib-' + self.version() + '.tar.bz2')

