class external_package:
	
	def packageneric(self):
		return self._packageneric
	
	def debian(self):
		return self._debian
		
	def pkg_config(self):
		return self._pkg_config
	def _check_pkg_config(self):
		return_code, output = self.packageneric().configure().packageneric__pkg_config(self.packageneric(), self.pkg_config(), 'exists')
		return return_code

	def depends(self):
		return self._depends
	def add_depend(self, depend):
		self._depends.append(depend)
	def add_depends(self, depends):
		for x in depends:
			self.add_depend(x)

	def builds(self):
		return self._builds
	def add_build(self, library, header, call = ';', language = 'C++'):
		class build:
			def __init__(self, library = None, header = None, call = ';', language = 'C++'):
				self._library = library
				self._header = header
				self._call = call
				self._language = language
			def library(self):
				return self._library
			def header(self):
				return self._header
			def call(self):
				return self._call
			def language(self):
				return self._language
		self._builds.append(build(library, header, call, language))
	def _check_build(self, libraries, headers, calls = ';', language = 'C++'):
		return self.packageneric().configure().CheckLibWithHeader(libs = libraries, header = headers, call = calls, language = language, autoadd = True)

	def frees(self):
		return self._frees
	def add_free(self, free):
		self._frees.append(free)
	def add_frees(self, frees):
		for x in frees:
			self.add_free(x)
	def _check_free(self, free):
		return self.packageneric().configure().packageneric__free(self.packageneric(), free)
	
	def try_run(self, description, text, language = '.cpp'):
			return_code, output = self.packageneric().configure().packageneric__try_run(self.packageneric(), description, text, language)
			return return_code, output
			
	def __init__(
		self,
		packageneric,
		debian,
		pkg_config = None,
		depends = None,
		builds = None,
		frees = None
	):
		self._packageneric = packageneric
		self._debian = debian
		self._pkg_config = pkg_config
		if not depends is None:
			self._depends = depends
		else:
			self._depends = []
		self._builds = []
		if not builds is None:
			for x in builds:
				if len(x) == 3:
					self.add_build(x[0], x[1], x[2])
				else:
					self.add_build(x[0], x[1], x[2], x[3])
		if not frees is None:
			self._frees = frees
		else:
			self._frees = []
		self._found = None
		self._environment = None
		
	def __str__(self):
		string = ''
		if not self.pkg_config() is None:
			string += self.pkg_config()
		else:
			string += self.debian()
		for x in self.builds():
			string += ' ' + x.library() + ' ' + x.header()
		return string
	
	def show(self):
		self.packageneric().information('external package: ' + str(self))
		
	def found(self):
		if self._found is None:
			self._found = True
			for x in self.depends():
				self._found &= x.found()
			if not self.pkg_config() is None:
				self._found &= self._check_pkg_config()
			for x in self.builds():
				self._found &= self._check_build(x.library(), x.header(), x.call(), x.language())
			for x in self.frees():
				self._found &= self._check_free(x)
		return self._found
		
	def environment(self):
		if not self.found():
			self.packageneric().error(str(self) + ': cannot generate environment because dependencies were not found')
		if self._environment is None:
			self._environment = self.packageneric().environment().Copy()
			if not self.pkg_config() is None:
				self._environment.ParseConfig('pkg-config --cflags --libs \'' + self.pkg_config() + '\'')
		return self._environment
