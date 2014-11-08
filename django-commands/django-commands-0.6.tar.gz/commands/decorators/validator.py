class validator(object):
	"""
		The validator decorator is a method decorator that specifies
		a key and an error message indicating which data parameter
		the method validates and what the error message should be
		if the validation fails.
	"""

	def __init__(self, key, error):
		self.key = key
		self.error = error

	def __call__(self, func):
		func.validator = True
		func.key = self.key
		func.error = self.error
		return func