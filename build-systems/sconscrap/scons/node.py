# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

class node:
	def __init__(
		self,
		dependencies = None
	):
		self._dependencies = []
		self.add_dependencies(dependencies)
		self._visiting = False

	def dependencies(self): return self._dependencies
	def add_dependencies(self, nodes):
		if nodes is not None:
			for node in nodes: self.add_dependency(node)
	def add_dependency(self, node_):
		assert isinstance(node_, node)
		if node_ not in self._dependencies: self._dependencies.append(node_)

	def dynamic_dependencies(self):
		'to be overridden in derived classes'
		pass
	
	def result(self):
		try: return self._result
		except AttributeError:
			self.dynamic_dependencies()
			self._visiting = True
			self._result = True
			self._failed_dependencies = []
			for node in self.dependencies():
				if node._visiting: raise node # cycle detected
				if not node.result():
					self._result = False
					self._failed_dependencies.append(node)
			self._visiting = False
			self._result = self._result and self.execute()
			return self._result

	def failed_dependencies(self):
		try: return self._failed_dependencies
		except AttributeError:
			self.result()
			return self._failed_dependencies
		
	def leaf_failed_dependencies(self):
		nodes = []
		for node in self.failed_dependencies():
			if not node.failed_dependencies():
				if not node in nodes: nodes.append(node)
			else:
				for node in node.leaf_failed_dependencies():
					if not node in nodes: nodes.append(node)
		return nodes

	def execute(self):
		'to be overridden in derived classes'
		return True
