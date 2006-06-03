class pkg_config_package:
	def __init__(
		self,
		packageneric,
		name = None,
		version = None,
		description = '',
		modules = None
	):
		self._packageneric = packageneric
		self._name = name
		self._version = version
		self._description = description
		if modules is None:
			self._modules = []
		else:
			self._modules = modules
		
	def packageneric(self):
		return self._packageneric
		
	def name(self):
		return self._name
		
	def version(self):
		return self._version
	
	def description(self):
		return self._description
		
	def modules(self):
		return self._modules
		
	def build_depends(self):
		packages = []
		for module in self.modules():
			for package in module.build_depends() + module.depends():
				if not package in packages:
					packages.append(package)
		return packages

	def pc(self):
		'''
		prefix=/home/bohan/work/dev/++packageneric/install
		exec_prefix=${prefix}
		pkgversion=0.0.20060512
		pkgnameversion=universalis-${pkgversion}
		pkgversionlibdir=${exec_prefix}/lib/${pkgnameversion}
		pkgversionincludedir=${prefix}/include/${pkgnameversion}
		pkgversionsharedincludedir=${prefix}/share/include/${pkgnameversion}

		Name: universalis 0:0:0 i686-pc-linux-gnu
		Description: universalis platform abstraction layer
		Version: ${pkgversion}
		Cflags: -I${prefix}/include -I${pkgversionincludedir}   
		Libs: -L${exec_prefix}/lib -L${pkgversionlibdir} -l-universalis  -lboost_thread -lboost_filesystem -lboost_signals 
		Requires:  diversalis >= 0.0.0 glibmm-2.4 >= 2.4 gthread-2.0 >= 2.0
		'''
		string = 'prefix=' + self.packageneric().environment().subst('$packageneric__install_prefix') + '\n'
		string += 'Name: ' + self.name() + ' ' + str(self.version()) + '\n'
		string += 'Description: ' + self.description() + '\n'
		string += 'Version: ' + str(self.version()) + '\n' # todo module *interface* version, not package one
		string += 'CFlags: ' + self.packageneric().environment().subst('$CXXFLAGS') + '\n'
		string += 'Libs: ' + self.packageneric().environment().subst('$LINKFLAGS')
		for library in self.packageneric().environment().Split(self.packageneric().environment().subst('$LIBS')):
			string += ' -l' + library
		string += '\n'
		string += 'Libs.private: ' + '\n'
		string += 'Requires: '
		for package in self.build_depends():
			if package.pkg_config():
				string += package.pkg_config() + ', '
		string += '\n'
		#self.packageneric().environment().Alias(self.name() + '.pc', ...)
		return string
