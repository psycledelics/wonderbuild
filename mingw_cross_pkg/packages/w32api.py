import os
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
