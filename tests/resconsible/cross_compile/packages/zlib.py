import os
from packages import Package

def package(packages): return ZLib(packages)

class ZLib(Package):
	def __init__(self, packages):
		Package.__init__(self, packages, 'zlib', '1.2.3')
		self.add_dep('gcc')

	def description(self): return 'compression library'

	def _tarball(self): return self._dir() + '.tar.bz2'
	def _dir(self): return self.name() + '-' + self.version()
	
	def download(self): self.http_get(self.mirror('sourceforge') + '/libpng/' + self._tarball())

	def clean_download(self): os.unlink(self._tarball())
	
	def build(self):
		self.shell('tar xjf ' + self._tarball())
		self.shell(
			'cd ' + self._dir() + ' && \n'
			# zlib doesn't use autotools and its makefile doesn't support destdir.
			# We cheat by setting prefix to destdir (it's ok since there's no rpath).
			'CC=' + self.target() + '-gcc \\\n'
			'RANLIB=' + self.target() + '-ranlib \\\n'
			'./configure \\\n'
				'--prefix=' + os.path.join(self.dest_dir() + self.prefix(), self.target())
		)
		self.continue_build()

	def continue_build(self):
		self.shell(self.gmake() + ' -C ' + self._dir() + ' install')
	
	def clean_build(self):
		self.shell('rm -Rf ' + self._dir())

