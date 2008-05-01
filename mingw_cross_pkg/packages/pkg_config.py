# pkg-config package recipee for MinGW cross pkg tool.
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
from packages import PackageRecipee

def package(packages): return PkgConfig(packages)

class PkgConfig(PackageRecipee):
	def __init__(self, packages):
		PackageRecipee.__init__(self, packages, 'pkg_config', '0.23')
		self.add_dep('gcc')

	def description(self): return 'manage compile and link flags for libraries'
	
	def _tarball(self): return self._dir() + '.tar.gz'
	def _dir(self): return 'pkg-config-' + self.version()

	def download(self): self.http_get('pkgconfig.freedesktop.org/releases/' + self._tarball())

	def build(self):
		self.shell('tar xzf ' + self._tarball())
		self.shell(
			'cd ' + self._dir() + ' && \n'
			'./configure \\\n'
				'--prefix=' + os.path.join(self.prefix(), self.target())
		)
		self.continue_build()

	def continue_build(self):
		self.shell(self.gmake() + ' -C ' + self._dir() + ' install DESTDIR=' + self.dest_dir())
		self.shell('install -d ' + os.path.join(self.dest_dir() + self.prefix(), 'bin'))
		f = os.path.join(self.dest_dir() + self.prefix(), 'bin', self.target() + '-pkg-config')
		if os.path.exists(f): os.unlink(f)
		self.shell('ln -s ' + os.path.join(os.pardir, self.target(), 'bin', 'pkg-config') + ' ' + f)
	
	def clean_build(self):
		if os.path.exists(self._dir()): shutil.rmtree(self._dir())

