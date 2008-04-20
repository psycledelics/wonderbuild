import os
from packages import Package

def package(packages): return Gcc(packages)

class Gcc(Package):
	def __init__(self, packages):
		Package.__init__(self, packages, 'gcc', '4.2.1-2')
		self.add_dep('binutils')
		self.add_dep('w32api')
		self.add_dep('mingw_runtime')

	def description(self): return 'The GNU Compiler Collection'

	def download(self): self.http_get(self.mirror('sourceforge') + '/mingw/gcc-' + self.version() + '-src.tar.gz')

