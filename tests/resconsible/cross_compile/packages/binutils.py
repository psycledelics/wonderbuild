import os
from packages import Package

def package(packages): return BinUtils(packages)

class BinUtils(Package):
	def __init__(self, packages):
		Package.__init__(self, packages, 'binutils', self._version_short() + '-20080109')
	
	def _version_short(self): return '2.18.50'
	
	def description(self): return 'The GNU assembler, linker and binary utilities'

	def _tarball(self): return 'binutils-' + self.version() + '-src.tar.gz'
	
	def download(self): self.http_get(self.mirror('sourceforge') + '/mingw/' + self._tarball())

	def clean_download(self): self.shell('rm -f ' + self._tarball())
	
	def build(self):
		self.shell('tar fzx ' + self._tarball())
		self.shell(
			'cd binutils-' + self._version_short() + ' && \n'
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
		self.shell(self.gmake() + ' -C binutils-' + self._version_short() + ' all install DESTDIR=' + self.destdir())
	
	def clean_build(self):
		self.shell('rm -Rf binutils-' + self._version_short())

