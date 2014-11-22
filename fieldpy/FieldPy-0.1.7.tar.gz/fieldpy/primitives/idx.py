"""
This module contains point primitive classes
"""

from __future__ import division
import numpy

class idx3D(object):
	r"""A 3D index class"""
	
	def __init__(self, indices):
		r"""Class constructor
		
		This method creates and returns a 'idx3D' object from another type
		of object which may be a list, a tuple, an one-dimensional
		numpy.ndarray, or even a 'idx3D' object
		
		Parameters:
			indices (list, a tuple, a numpy.ndarray, or idx3D): The object
				to be converted to 'idx3D'
		"""
		
		if type(indices) == type(self):
			self.i = indices.i
			self.j = indices.j
			self.k = indices.k
			return
		
		if (type(indices) == list) or (type(indices) == tuple):
			if len(indices) < 3:
				raise ValueError("At least 3 entries are needed")
		elif type(indices) == numpy.ndarray:
			if len(indices.shape) != 1:
				raise ValueError("NumPy arrays must be one-dimensional")
		else:
			raise TypeError("Invalid index type")
		
		self.i = indices[0]
		self.j = indices[1]
		self.k = indices[2]
		
	def __str__(self):
		r"""Returns a string representation of the object"""
		
		return '[%d, %d, %d]' % (self.i, self.j, self.k)
		
	def __repr__(self):
		r"""Returns a string representation of the object"""
		
		return self.__str__()
	
	def __eq__(self, other):
		r"""Checks if the two 'idx3D' objects have equal indices
		
		This method checks if the two arguments are both of 'idx3D' type
		and	if they are it then compares the indices. If they are equal it
		returns	"True". If the 'other' object is not of the same type or if the
		coordinates are not equal it returns "False"
		
		Parameters:
			other (idx3D): The other 'idx3D' point against which the
				comparison is performed
		
		Returns:
			"True" if both arguments are of 'idx3D' type and their
			indices are equal otherwise "False"
		"""
		
		#if both objects are of 'idx3D' type then...
		if type(self) == type(other): #...add their respective indices
			return (self.i == other.i) and (self.j == other.j) and (self.k == other.k)
		else:
			return False
	
	def __add__(self, other):
		r"""Addition overloader (multiple 'type' support)
		
		This method overloads the '+' operator and allows for the indices of
		a 'idx3D' object to be added to either those of another object of
		the same type or to a list, a tuple, or even to a single int
		
		Parameters:
			other (pointCart3D, list, tuple, or int): Another 'idx3D'
				object, a list/tuple with (at least) 3 values, or a single int
		"""
		
		if type(self) == type(other):
			return idx3D([self.i + other.i, self.j + other.j, self.k + other.k])
		elif (type(other) == list) or (type(other) == tuple):
			return idx3D([self.i + other[0], self.j + other[1], self.k + other[2]])
		elif (type(other) == int):
			return idx3D([self.i + other, self.j + other, self.k + other])
		else:
			raise TypeError("Can't add '" + str(other) + "' and '" + str(self) + "'")
		
	def __sub__(self, other):
		r"""Subtraction overloader (multiple 'type' support)
		
		This method overloads the '-' operator and allows for the indices of
		a 'idx3D' object to be subtracted with either those of another object
		of the same type or with a list, a tuple, or even with a single int
		
		Parameters:
			other (idx3D, list, tuple, or int): Another 'idx3D'
				object, a list/tuple with (at least) 3 values, or a single int
		"""
		
		if type(self) == type(other):
			return idx3D([self.i - other.i, self.j - other.j, self.k - other.k])
		elif (type(other) == list) or (type(other) == tuple):
			return idx3D([self.i - other[0], self.j - other[1], self.k - other[2]])
		elif (type(other) == int):
			return idx3D([self.i - other, self.j - other, self.k - other])
		else:
			raise TypeError("Can't subtract '" + str(other) + "' and '" + str(self) + "'")
		
	def toList(self):
		r"""Converts a 'idx3D' object into a 'list'
		
		This method creates and returns a 'list' object from the reference
		'idx3D' object
		
		Returns:
			A 'list' object with the 'idx3D' object's 'i', 'j', and 'k'
			attributes as entries
		"""
		
		#return a list with the 'idx3D' indices
		return [self.i, self.j, self.k]
	
	def toTuple(self):
		r"""Converts a 'idx3D' object into a 'tuple'
		
		This method creates and returns a 'tuple' object from the reference
		'idx3D' object

		Returns:
			A 'tuple' object with the 'idx3D' object's 'i', 'j', and 'k'
			attributes as entries
		"""
		
		#return a list with the 'idx3D' indices
		return (self.i, self.j, self.k)
	
class idx2D(object):
	r"""A 2D index class"""
	
	def __init__(self, indices):
		r"""Class constructor
		
		This method creates and returns a 'idx2D' object from another type
		of object which may be a list, a tuple, an one-dimensional
		numpy.ndarray, or even a 'idx2D' object
		
		Parameters:
			indices (list, a tuple, a numpy.ndarray, or idx2D): The object
				to be converted to 'idx2D'
		"""
		
		if type(indices) == type(self):
			self.i = indices.i
			self.j = indices.j
			return
		
		if (type(indices) == list) or (type(indices) == tuple):
			if len(indices) < 2:
				raise ValueError("At least 2 entries are needed")
		elif type(indices) == numpy.ndarray:
			if len(indices.shape) != 1:
				raise ValueError("NumPy arrays must be one-dimensional")
		else:
			raise TypeError("Invalid index type")
		
		self.i = indices[0]
		self.j = indices[1]
		
	def __str__(self):
		r"""Returns a string representation of the object"""
		
		return '[%d, %d]' % (self.i, self.j)
		
	def __repr__(self):
		r"""Returns a string representation of the object"""
		
		return self.__str__()
	
	def __eq__(self, other):
		r"""Checks if the two 'idx2D' objects have equal indices
		
		This method checks if the two arguments are both of 'idx2D' type
		and	if they are it then compares the indices. If they are equal it
		returns	"True". If the 'other' object is not of the same type or if the
		coordinates are not equal it returns "False"
		
		Parameters:
			other (idx2D): The other 'idx2D' point against which the
				comparison is performed
		
		Returns:
			"True" if both arguments are of 'idx2D' type and their
			indices are equal otherwise "False"
		"""
		
		#if both objects are of 'idx2D' type then...
		if type(self) == type(other): #...add their respective indices
			return (self.i == other.i) and (self.j == other.j)
		else:
			return False
	
	def __add__(self, other):
		r"""Addition overloader (multiple 'type' support)
		
		This method overloads the '+' operator and allows for the indices of
		a 'idx2D' object to be added to either those of another object of
		the same type or to a list, a tuple, or even to a single int
		
		Parameters:
			other (pointCart2D, list, tuple, or int): Another 'idx2D'
				object, a list/tuple with (at least) 2 values, or a single int
		"""
		
		if type(self) == type(other):
			return idx2D([self.i + other.i, self.j + other.j])
		elif (type(other) == list) or (type(other) == tuple):
			return idx2D([self.i + other[0], self.j + other[1]])
		elif (type(other) == int):
			return idx2D([self.i + other, self.j + other])
		else:
			raise TypeError("Can't add '" + str(other) + "' and '" + str(self) + "'")
		
	def __sub__(self, other):
		r"""Subtraction overloader (multiple 'type' support)
		
		This method overloads the '-' operator and allows for the indices of
		a 'idx2D' object to be subtracted with either those of another object
		of the same type or with a list, a tuple, or even with a single int
		
		Parameters:
			other (idx2D, list, tuple, or int): Another 'idx2D'
				object, a list/tuple with (at least) 2 values, or a single int
		"""
		
		if type(self) == type(other):
			return idx2D([self.i - other.i, self.j - other.j])
		elif (type(other) == list) or (type(other) == tuple):
			return idx2D([self.i - other[0], self.j - other[1]])
		elif (type(other) == int):
			return idx2D([self.i - other, self.j - other])
		else:
			raise TypeError("Can't subtract '" + str(other) + "' and '" + str(self) + "'")
		
	def toList(self):
		r"""Converts a 'idx2D' object into a 'list'
		
		This method creates and returns a 'list' object from the reference
		'idx2D' object
		
		Returns:
			A 'list' object with the 'idx2D' object's 'i' and 'j'
			attributes as entries
		"""
		
		#return a list with the 'idx2D' indices
		return [self.i, self.j]
	
	def toTuple(self):
		r"""Converts a 'idx2D' object into a 'tuple'
		
		This method creates and returns a 'tuple' object from the reference
		'idx2D' object

		Returns:
			A 'tuple' object with the 'idx2D' object's 'i' and 'j'
			attributes as entries
		"""
		
		#return a list with the 'idx2D' indices
		return (self.i, self.j)