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
		result = []
		for module in self.modules():
			for package in module.build_depends() + module.depends():
				if not package.debian() in result:
					result.append(package.debian())
		return result
