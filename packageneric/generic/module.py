import os

class module:
	class types:
		files = 'files'
		shared_lib = 'shared_lib'
		static_lib = 'static_lib'
		bin = 'bin'
		python = 'python'
		
	def __init__(
		self, 
		packageneric, 
		name = None,
		version = None,
		description = '',
		depends = None,
		build_depends = None
	):
		self._packageneric = packageneric
		self._name = name
		self._version = version
		self._description = description
		if depends is None:
			self._depends = []
		else:
			self._depends = depends
		if build_depends is None:
			self._build_depends = []
		else:
			self._build_depends = build_depends
		self._sources = []
		self._headers = []
		self._include_path = []
		self._defines = {}
		self._environment = None
		self._targets = None
	
	def packageneric(self):
		return self._packageneric
		
	def name(self):
		return self._name
	
	def version(self):
		return self._version
	
	def description(self):
		return self._description
		
	def sources(self):
		return self._sources
	def add_source(self, source):
		self.sources().append(os.path.join(self.packageneric().build_directory(), source))
	def add_sources(self, sources):
		for x in sources: self.add_source(x)
		
	def headers(self):
		return self._headers
	def add_header(self, header):
		self.headers().append(header)
	def add_headers(self, headers):
		for x in headers: self.add_header(x)
		
	def include_path(self):
		return self._include_path
	def add_include_path(self, path):
		self._include_path.append(path)
	
	def defines(self):
		return self._defines
	def add_define(self, name, value):
		self._defines.append({name: value})
		
	def depends(self):
		packages = []
		for package in self._depends:
			if not package in packages:
				packages.append(package)
			for package in package.depends():
				if not package in packages:
					packages.append(package)
		return packages
	def add_depend(self, depend):
		self._depends.append(depend)
	def add_depends(self, depends):
		for package in depends:
			self.add_depend(package)
		
	def build_depends(self):
		packages = []
		for package in self._build_depends:
			if not package in packages:
				packages.append(package)
			for package in package.depends():
				if not package in packages:
					packages.append(package)
		return packages
	def add_build_depend(self, build_depend):
		self._build_depends.append(build_depend)
	def add_build_depends(self, build_depends):
		for package in build_depends:
			self.add_build_depend(package)
		
	def show(self, list_files = False):
		self.packageneric().information('module: ' + self.name() + ' ' + str(self.version()))
		depends = []
		for package in self.depends():
			depends.append(str(package))
		self.packageneric().information('module: depends: ' + str(depends))
		build_depends = []
		for package in self.build_depends():
			build_depends.append(str(package))
		self.packageneric().information('module: build depends: ' + str(build_depends))
		if list_files:
			self.packageneric().trace('module: sources:')
			self.packageneric().trace(str(self.sources()))
			self.packageneric().trace('module: headers:')
			self.packageneric().trace(str(self.headers()))
	
	def environment(self):
		if self._environment is None:
			self._environment = self.packageneric().environment().Copy()
			depends_not_found = []
			for package in self.build_depends() + self.depends():
				if not package.found():
					depends_not_found.append(str(package))
			if depends_not_found:
				self.packageneric().abort(self.name() + ': cannot generate environment because dependencies were not found: ' + str(depends_not_found))
			self._environment.Append(
				SHCXXCOMSTR = self.packageneric().message('compiling $TARGET'),
				SHLINKCOMSTR = self.packageneric().message('linking $TARGET')
			)
			self._environment.AppendUnique(CPPPATH = self.include_path())
			self._environment.Append(CPPDEFINES = self.defines())
			self._environment.Append(
				CPPDEFINES = {
					'PACKAGENERIC__MODULE__NAME': '\\"' + self.name() + '\\"',
					'PACKAGENERIC__MODULE__VERSION': '\\"' + str(self.version()) + '\\"'
				}
			)
			pkg_config = ''
			for package in self.build_depends() + self.depends():
				if not package.pkg_config() is None:
					pkg_config += ' ' + package.pkg_config()
			if not pkg_config == '':
				self._environment.ParseConfig('pkg-config --cflags --libs \'' + pkg_config + '\'')
		return self._environment
			
	def targets(self):
		if self._targets is None:
			self.environment()
			self.packageneric().finish_configure()
			self._targets = self.environment().SharedLibrary(os.path.join(self.packageneric().build_directory(), self.name()), self.sources())
			self.environment().Alias(self.name(), self._targets)
		return self._targets
