class distribution_archive:
	def __init__(
		self,
		packageneric,
		remote_path = None,
		source_packages = [],
		binary_packages = []
	):
		self._packageneric = packageneric
		self._remote_path = remote_path
		self._source_packages = source_packages
		self._binary_packages = binart_packages

	def packageneric(self):
		return self._packageneric
		
	def remote_path(self):
		return self._remote_path
		
	def source_packages(self):
		return self._source_packages
		
	def binary_packages(self):
		return self._binary_packages
