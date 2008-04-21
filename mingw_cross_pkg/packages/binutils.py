import os
from packages import Package

def package(packages): return BinUtils(packages)

class BinUtils(Package):
	def __init__(self, packages):
		Package.__init__(self, packages, 'binutils', self._version_short() + '-20080109')
	
	def _version_short(self): return '2.18.50'
	
	def description(self): return 'The GNU assembler, linker and binary utilities'

	def _tarball(self): return self.name() + '-' + self.version() + '-src.tar.gz'
	def _dir(self): return self.name() + '-' + self._version_short()
	
	def download(self): self.http_get(self.mirror('sourceforge') + '/mingw/' + self._tarball())

	def clean_download(self): os.unlink(self._tarball())
	
	def build(self):
		self.shell('tar xzf ' + self._tarball())
		self.shell(
			'cd ' + self._dir() + ' && \n'
			'./configure \\\n'
				'--target=' + self.target() + ' \\\n'
				'--prefix=' + self.prefix() + ' \\\n'
				'--with-gcc \\\n'
				'--with-gnu-ld \\\n'
				'--with-gnu-as \\\n'
				'--disable-nls \\\n'
				'--disable-shared'
		)
		self.continue_build()

	def continue_build(self):
		self.shell(self.gmake() + ' -C ' + self._dir() + ' all install DESTDIR=' + self.dest_dir())
	
	def clean_build(self):
		self.shell('rm -Rf ' + self._dir())

