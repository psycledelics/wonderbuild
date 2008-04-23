import os, shutil
from packages import PackageRecipee

def package(packages): return MingwRuntime(packages)

class MingwRuntime(PackageRecipee):
	def __init__(self, packages):
		PackageRecipee.__init__(self, packages, 'mingw_runtime', '3.14')
		
	def _tarball(self): return 'mingw-runtime-' + self.version() + '.tar.gz'

	def download(self): self.http_get(self.mirror('sourceforge') + '/mingw/' + self._tarball())

	def build(self):
		tar_dir = os.getcwd()
		dir = os.path.join(self.dest_dir() + self.prefix(), self.target())
		if not os.path.exists(dir): os.makedirs(dir)
		os.chdir(dir)
		self.shell('tar xzf ' + os.path.join(tar_dir, self._tarball()))

