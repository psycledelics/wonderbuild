import os
from packages import Package

def package(packages): return W32api(packages)

class W32api(Package):
	def __init__(self, packages):
		Package.__init__(self, packages, 'w32api', '3.11')

	def download(self): self.http_get(self.mirror('sourceforge') + '/mingw/w32api-' + self.version() + '.tar.gz')

