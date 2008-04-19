import os
from packages import Package

def package(packages): return MingwRuntime(packages)

class MingwRuntime(Package):
	def __init__(self, packages):
		Package.__init__(self, packages, 'mingw_runtime', '3.14')
		
	def download(self): self.http_get(self.mirror('sourceforge') + '/mingw/mingw-runtime-' + self.version() + '.tar.gz')

