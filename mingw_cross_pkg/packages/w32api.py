# w32api package for MinGW cross pkg tool.
# copyright 2008-2008 Johan Boule <bohan@jabber.org>
#
# Based on MinGW cross compiling environment (1.4)
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
from packages import Package

def package(packages): return W32api(packages)

class W32api(Package):
	def __init__(self, packages):
		Package.__init__(self, packages, 'w32api', '3.11')

	def _tarball(self): return self.name() + '-' + self.version() + '.tar.gz'

	def download(self): self.http_get(self.mirror('sourceforge') + '/mingw/' + self._tarball())

	def build(self):
		tar_dir = os.getcwd()
		dir = os.path.join(self.dest_dir() + self.prefix(), self.target())
		if not os.path.exists(dir): os.makedirs(dir)
		os.chdir(dir)
		self.shell('tar xzf ' + os.path.join(tar_dir, self._tarball()))
		self.shell(
	    	'# fix incompatibilities with gettext\n' + \
	    	self.gsed() + " 's,\\(SUBLANG_BENGALI_INDIA\\t\\)0x01,\\10x00,' -i " + os.path.join('include', 'winnt.h') + ' &&\n' + \
	    	self.gsed() + " 's,\\(SUBLANG_PUNJABI_INDIA\\t\\)0x01,\\10x00,' -i " + os.path.join('include', 'winnt.h') + '&&\n' + \
			self.gsed() + " 's,\\(SUBLANG_ROMANIAN_ROMANIA\\t\\)0x01,\\10x00,' -i " + os.path.join('include', 'winnt.h') + '&&\n' + \
			'# fix incompatibilities with jpeg\n' + \
			self.gsed() + " 's,typedef unsigned char boolean;,,' -i " + os.path.join('include', 'rpcndr.h') + '&&\n' + \
			'# fix missing definitions for WinPcap and libdnet\n' + \
			self.gsed() + " '1i\\#include <wtypes.h>' -i " + os.path.join('include', 'iphlpapi.h') + '&&\n' + \
			self.gsed() + " '1i\\#include <wtypes.h>' -i " + os.path.join('include', 'wincrypt.h') + '\n'
		)
