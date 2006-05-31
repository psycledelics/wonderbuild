class person:
	def __init__(
		self,
		name,
		email
	):
		self._name = name
		self._email = email
		
	def name(self):
		return self._name
	
	def email(self):
		return self._email
