class distribution_archive:
	def __init__(self, project,
		remote_path = None,
		source_packages = [],
		binary_packages = []
	):
		self._project = project
		self._remote_path = remote_path
		self._source_packages = source_packages
		self._binary_packages = binart_packages

	def project(self): return self._project
		
	def remote_path(self): return self._remote_path
		
	def source_packages(self): return self._source_packages
		
	def binary_packages(self): return self._binary_packages
