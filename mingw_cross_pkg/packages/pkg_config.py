import os
from packages import Package

def package(packages): return PkgConfig(packages)

class PkgConfig(Package):
	def __init__(self, packages):
		Package.__init__(self, packages, 'pkg_config', '0.22')
		self.add_dep('gcc')

	def description(self): return 'manage compile and link flags for libraries'
	
	def download(self): self.http_get('pkgconfig.freedesktop.org/releases/pkg-config-' + self.version() + '.tar.gz')


