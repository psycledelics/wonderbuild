# gcc package recipe for MinGW cross pkg tool.
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2008 Johan Boule <bohan@jabber.org>
#
# Based on MinGW cross compiling environment, version 1.4
# copyright 2007-2008 Volker Grabsch <vog@notjusthosting.com>
# copyright 2007-2008 Rocco Rutte <pdmef@gmx.net>
# copyright 2007-2008 Andreas Roever <roever@users.sf.net>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject
# to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os, shutil
from packages import PackageRecipe

def package(packages): return Gcc(packages)

class Gcc(PackageRecipe):
	def __init__(self, packages):
		PackageRecipe.__init__(self, packages, 'gcc', '4.2.1-2')
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

