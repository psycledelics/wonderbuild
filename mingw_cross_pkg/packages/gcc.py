import os, shutil
from packages import Package

def package(packages): return Gcc(packages)

class Gcc(Package):
	def __init__(self, packages):
		Package.__init__(self, packages, 'gcc', '4.2.1-2')
		self.add_dep('binutils')
		self.add_dep('mingw_runtime')
		self.add_dep('w32api')

	def description(self): return 'The GNU Compiler Collection'

	def _tarball(self): return self._dir() + '.tar.gz'
	def _dir(self): return self.name() + '-' + self.version() + '-src'

	def download(self): self.http_get(self.mirror('sourceforge') + '/mingw/' + self._tarball())

	def build(self):
		self.shell('tar xzf ' + self._tarball())
		self.shell(
			'cd ' + self._dir() + ' && \n'
			'./configure \\\n'
				'--target=' + self.target() + ' \\\n'
				'--prefix=' + self.prefix() + ' \\\n'
		        '--enable-languages="c,c++" \\\n'
		        '--enable-version-specific-runtime-libs \\\n'
		        '--with-gcc \\\n'
		        '--with-gnu-ld \\\n'
		        '--with-gnu-as \\\n'
		        '--disable-nls \\\n'
		        '--disable-shared \\\n'
		        '--without-x \\\n'
		        '--enable-threads=win32 \\\n'
		        '--disable-win32-registry \\\n'
		        '--enable-sjlj-exceptions'
		)
		self.continue_build()

	def continue_build(self):
		self.shell(self.gmake() + ' -C ' + self._dir() + ' all install DESTDIR=' + self.dest_dir())
	
	def clean_build(self):
		if os.path.exists(self._dir()): shutil.rmtree(self._dir())

