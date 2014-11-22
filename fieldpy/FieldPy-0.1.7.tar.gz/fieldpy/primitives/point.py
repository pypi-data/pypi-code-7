"""
This module contains point primitive classes
"""

from __future__ import division
import numpy

class pointCart3D(object):
	r"""A 3D cartesian point coordinates class"""
	
	def __init__(self, coords):
		r"""Class constructor and initialization
		
		This method creates and returns a 'pointCart3D' object from another type
		of object which may be a list, a tuple, or an one-dimensional
		numpy.ndarray. At least three entries must exist for this object to be
		initialized
		
		Parameters:
			coords (list, a tuple, a numpy.ndarray, or pointCart3D): The object
				to be converted to 'pointCart3D'
		"""
		
		if type(coords) == type(self):
			self.x = coords.x
			self.y = coords.y
			self.z = coords.z
			return
		
		if (type(coords) == list) or (type(coords) == tuple):
			if len(coords) < 3:
				raise ValueError("At least 3 entries are needed")
		elif type(coords) == numpy.ndarray:
			if len(coords.shape) != 1:
				raise ValueError("NumPy arrays must be one-dimensional")
		else:
			raise TypeError("Invalid coords type")
		
		self.x = coords[0]
		self.y = coords[1]
		self.z = coords[2]
		
	def __str__(self):
		r"""Returns a string representation of the object"""
		
		return '(%0.4f, %0.4f, %0.4f)' % (self.x, self.y, self.z)
		
	def __repr__(self):
		r"""Returns a string representation of the object"""
		
		return self.__str__()
	
	def __eq__(self, other):
		r"""Checks if the two 'pointCart3D' objects have equal coordinates
		
		This method checks if the two arguments are both of 'pointCart3D' type
		and	if they are it then compares the coordinates. If they are equal it
		returns	"True". If the 'other' object is not of the same type or if the
		coordinates are not equal it returns "False"
		
		Parameters:
			other (pointCart3D): The other 'pointCart3D' point against which the
				comparison is performed
		
		Returns:
			"True" if both arguments are of 'pointCart3D' type and their
			coordinates are equal otherwise "False"
		"""
		
		#if both  objects are of 'pointCart3D' type then...
		if type(self) == type(other): #...add their respective coordinates
			return (self.x == other.x) and (self.y == other.y) and (self.z == other.z)
		else:
			return False
	
	def __add__(self, other):
		r"""Addition overloader (multiple 'type' support)
		
		This method overloads the '+' operator and allows for the coordinates of
		a 'pointCart3D' object to be added to either those of another object of
		the same type or to a list, a tuple, or even to a single float
		
		Parameters:
			other (pointCart3D, list, tuple, or float): Another 'pointCart3D'
				object, a list/tuple with (at least) 3 values, or a single float
		"""
		
		if type(self) == type(other):
			return pointCart3D([self.x + other.x, self.y + other.y, self.z + other.z])
		elif (type(other) == list) or (type(other) == tuple):
			return pointCart3D([self.x + other[0], self.y + other[1], self.z + other[2]])
		elif numpy.isreal(other):
			return pointCart3D([self.x + other, self.y + other, self.z + other])
		else:
			raise TypeError("Can't add '" + str(other) + "' and '" + str(self) + "'")
		
	def __sub__(self, other):
		r"""Subtraction overloader (multiple 'type' support)
		
		This method overloads the '-' operator and allows for the coordinates of
		a 'pointCart3D' object to be subtracted with either those of another object
		of the same type or with a list, a tuple, or even with a single float
		
		Parameters:
			other (pointCart3D, list, tuple, or float): Another 'pointCart3D'
				object, a list/tuple with (at least) 3 values, or a single float
		"""
		
		if type(self) == type(other):
			return pointCart3D([self.x - other.x, self.y - other.y, self.z - other.z])
		elif (type(other) == list) or (type(other) == tuple):
			return pointCart3D([self.x - other[0], self.y - other[1], self.z - other[2]])
		elif numpy.isreal(other):
			return pointCart3D([self.x - other, self.y - other, self.z - other])
		else:
			raise TypeError("Can't subtract '" + str(other) + "' and '" + str(self) + "'")
	
	def __mul__(self, other):
		r"""Multiplication overloader (multiple 'type' support)
		
		This method overloads the '*' operator and allows for the coordinates of
		a 'pointCart3D' object to be multiplied with either those of another
		object of the same type or with a list, a tuple, or even with a single
		float
		
		Parameters:
			other (pointCart3D, list, tuple, or float): Another 'pointCart3D'
				object, a list/tuple with (at least) 3 values, or a single float
		"""
		
		if type(self) == type(other):
			return pointCart3D([self.x * other.x, self.y * other.y, self.z * other.z])
		elif (type(other) == list) or (type(other) == tuple):
			return pointCart3D([self.x * other[0], self.y * other[1], self.z * other[2]])
		elif numpy.isreal(other):
			return pointCart3D([self.x * other, self.y * other, self.z * other])
		else:
			raise TypeError("Can't multiply '" + str(other) + "' and '" + str(self) + "'")

	def __div__(self, other):
		r"""Division overloader (multiple 'type' support)

		This method overloads the '/' operator and allows for the coordinates of
		a 'pointCart3D' object to be divided with either those of another object
		of the same type or with a list, a tuple, or even with a single float

		Parameters:
			other (pointCart3D, list, tuple, or float): Another 'pointCart3D'
				object, a list/tuple with (at least) 3 values, or a single float
		"""

		if type(self) == type(other):
			return pointCart3D([self.x / other.x, self.y / other.y, self.z / other.z])
		elif (type(other) == list) or (type(other) == tuple):
			return pointCart3D([self.x / other[0], self.y / other[1], self.z / other[2]])
		elif numpy.isreal(other):
			return pointCart3D([self.x / other, self.y / other, self.z / other])
		else:
			raise TypeError("Can't divide '" + str(other) + "' and '" + str(self) + "'")

	def __truediv__(self, other):
		r"""Division overloader (multiple 'type' support)
		
		This method overloads the '/' operator and allows for the coordinates of
		a 'pointCart3D' object to be divided with either those of another object
		of the same type or with a list, a tuple, or even with a single float
		
		Parameters:
			other (pointCart3D, list, tuple, or float): Another 'pointCart3D'
				object, a list/tuple with (at least) 3 values, or a single float
		"""
		
		if type(self) == type(other):
			return pointCart3D([self.x / other.x, self.y / other.y, self.z / other.z])
		elif (type(other) == list) or (type(other) == tuple):
			return pointCart3D([self.x / other[0], self.y / other[1], self.z / other[2]])
		elif numpy.isreal(other):
			return pointCart3D([self.x / other, self.y / other, self.z / other])
		else:
			raise TypeError("Can't divide '" + str(other) + "' and '" + str(self) + "'")

	def __floordiv__(self, other):
		r"""Division overloader (multiple 'type' support)

		This method overloads the '/' operator and allows for the coordinates of
		a 'pointCart3D' object to be divided with either those of another object
		of the same type or with a list, a tuple, or even with a single float

		Parameters:
			other (pointCart3D, list, tuple, or float): Another 'pointCart3D'
				object, a list/tuple with (at least) 3 values, or a single float
		"""

		if type(self) == type(other):
			return pointCart3D([self.x // other.x, self.y // other.y, self.z // other.z])
		elif (type(other) == list) or (type(other) == tuple):
			return pointCart3D([self.x // other[0], self.y // other[1], self.z // other[2]])
		elif numpy.isreal(other):
			return pointCart3D([self.x // other, self.y // other, self.z // other])
		else:
			raise TypeError("Can't divide '" + str(other) + "' and '" + str(self) + "'")

	def __abs__(self):
		r"""Returns the mangitude of the point as if it was a vector
		
		This method overloads the 'abs' function and calculates the magnitude of
		the 'pointCart3D' as if it was representing a vector. The returned
		result if the square root of the sum of squares of 'x', 'y', and 'z'
		"""
		
		return numpy.sqrt(self.x ** 2  +  self.y ** 2  +  self.z ** 2)

	@staticmethod
	def calcMidPoint(pointA, pointB):
		r"""Returns the midpoint between two points

		This method calculates the coordinates of the midpoint between two
		'pointCart3D' objects and returns a new 'pointCart3D' point with those
		coordinates

		Parameters:
			pointA (pointCart3D): A 'pointCart3D' object of the first point
			pointB (pointCart3D): A 'pointCart3D' object of the second point

		Returns:
			A 'pointCart3D' object representing the midpoint
		"""

		return pointCart3D([pointA.x + (pointB.x-pointA.x)/2.0,
		                    pointA.y + (pointB.y-pointA.y)/2.0,
		                    pointA.z + (pointB.z-pointA.z)/2.0])

	@staticmethod
	def calcDistanceSqrd(pointA, pointB):
		r"""Calculates the squared distance between two points
		
		This method calculates and returns the square of the Eucledian distance
		between two 'pointCart3D' objects
		
		Parameters:
			pointA (pointCart3D): A 'pointCart3D' object of the first point
			pointB (pointCart3D): A 'pointCart3D' object of the second point
		
		Returns:
			A float denoting the eucledian distance between the two points
		"""
		
		p = pointB - pointA
		return (p.x ** 2  +  p.y ** 2  +  p.z ** 2)
		
	@staticmethod
	def calcDistance(pointA, pointB):
		r"""Calculates the distance between two points
		
		This method calculates and returns the Eucledian distance between two
		'pointCart3D' objects
		
		Parameters:
			pointA (pointCart3D): A 'pointCart3D' object of the first point
			pointB (pointCart3D): A 'pointCart3D' object of the second point
		
		Returns:
			A float denoting the eucledian distance between the two points
		"""
		return numpy.sqrt(pointCart3D.calcDistanceSqrd(pointA, pointB))
	
	def toList(self):
		r"""Converts a 'pointCart3D' object into a 'list'
		
		This method creates and returns a 'list' object from the reference
		'pointCart3D' object

		Returns:
			A 'list' object with the 'pointCart' object's 'x', 'y', and 'z'
			attributes as entries
		"""
		
		#return a list with the 'pointCart3D' coordinates
		return [self.x, self.y, self.z]
	
	def toTuple(self):
		r"""Converts a 'pointCart3D' object into a 'tuple'
		
		This method creates and returns a 'tuple' object from the reference
		'pointCart3D' object

		Returns:
			A 'tuple' object with the 'pointCart' object's 'x', 'y', and 'z'
			attributes as entries
		"""
		
		#return a 'tuple' with the 'pointCart3D' coordinates
		return (self.x, self.y, self.z)


class pointCart2D(object):
	r"""A 2D cartesian point coordinates class"""
	
	def __init__(self, coords):
		r"""Class constructor
		
		This method creates and returns a 'pointCart2D' object from another type
		of object which may be a list, a tuple, or an one-dimensional
		numpy.ndarray. At least two entries must exist for this object to be
		initialized
		
		Parameters:
			coords (list, a tuple, or a numpy.ndarray): The object to be
				converted to 'pointCart2D'
		"""
		
		if type(coords) == type(self):
			self.x = coords.x
			self.y = coords.y
			return
		
		if (type(coords) == list) or (type(coords) == tuple):
			if len(coords) < 2:
				raise ValueError("At least 2 entries are needed")
		elif type(coords) == numpy.ndarray:
			if len(coords.shape) != 1:
				raise ValueError("NumPy arrays must be one-dimensional")
		else:
			raise TypeError("Invalid coords type")
		
		self.x = coords[0]
		self.y = coords[1]
		
	def __str__(self):
		r"""Returns a string representation of the object"""
		
		return '(%0.4f, %0.4f)' % (self.x, self.y)
		
	def __repr__(self):
		r"""Returns a string representation of the object"""
		
		return self.__str__()
	
	def __eq__(self, other):
		r"""Checks if the two 'pointCart2D' objects have equal coordinates
		
		This method checks if the two arguments are both of 'pointCart2D' type
		and	if they are it then compares the coordinates. If they are equal it
		returns	"True". If the 'other' object is not of the same type or if the
		coordinates are not equal it returns "False"
		
		Parameters:
			other (pointCart2D): The other 'pointCart2D' point against which the
				comparison is performed
		
		Returns:
			"True" if both arguments are of 'pointCart2D' type and their
			coordinates are equal otherwise "False"
		"""
		
		#if both  objects are of 'pointCart2D' type then...
		if type(self) == type(other): #...add their respective coordinates
			return (self.x == other.x) and (self.y == other.y)
		else:
			return False
	
	def __add__(self, other):
		r"""Addition overloader (multiple 'type' support)
		
		This method overloads the '+' operator and allows for the coordinates of
		a 'pointCart2D' object to be added to either those of another object of
		the same type or to a list, a tuple, or even to a single float
		
		Parameters:
			other (pointCart2D, list, tuple, or float): Another 'pointCart2D'
				object, a list/tuple with (at least) 2 values, or a single float
		"""
		
		if type(self) == type(other):
			return pointCart2D([self.x + other.x, self.y + other.y])
		elif (type(other) == list) or (type(other) == tuple):
			return pointCart2D([self.x + other[0], self.y + other[1]])
		elif numpy.isreal(other):
			return pointCart2D([self.x + other, self.y + other])
		else:
			raise TypeError("Can't add '" + str(other) + "' and '" + str(self) + "'")
		
	def __sub__(self, other):
		r"""Subtraction overloader (multiple 'type' support)
		
		This method overloads the '-' operator and allows for the coordinates of
		a 'pointCart2D' object to be subtracted with either those of another object
		of the same type or with a list, a tuple, or even with a single float
		
		Parameters:
			other (pointCart2D, list, tuple, or float): Another 'pointCart2D'
				object, a list/tuple with (at least) 2 values, or a single float
		"""
		
		if type(self) == type(other):
			return pointCart2D([self.x - other.x, self.y - other.y])
		elif (type(other) == list) or (type(other) == tuple):
			return pointCart2D([self.x - other[0], self.y - other[1]])
		elif numpy.isreal(other):
			return pointCart2D([self.x - other, self.y - other])
		else:
			raise TypeError("Can't subtract '" + str(other) + "' and '" + str(self) + "'")
	
	def __mul__(self, other):
		r"""Multiplication overloader (multiple 'type' support)
		
		This method overloads the '*' operator and allows for the coordinates of
		a 'pointCart2D' object to be multiplied with either those of another
		object of the same type or with a list, a tuple, or even with a single
		float
		
		Parameters:
			other (pointCart2D, list, tuple, or float): Another 'pointCart2D'
				object, a list/tuple with (at least) 2 values, or a single float
		"""
		
		if type(self) == type(other):
			return pointCart2D([self.x * other.x, self.y * other.y])
		elif (type(other) == list) or (type(other) == tuple):
			return pointCart2D([self.x * other[0], self.y * other[1]])
		elif numpy.isreal(other):
			return pointCart2D([self.x * other, self.y * other])
		else:
			raise TypeError("Can't multiply '" + str(other) + "' and '" + str(self) + "'")
		
	def __div__(self, other):
		r"""Division overloader (multiple 'type' support)
		
		This method overloads the '/' operator and allows for the coordinates of
		a 'pointCart2D' object to be divided with either those of another object
		of the same type or with a list, a tuple, or even with a single float
		
		Parameters:
			other (pointCart2D, list, tuple, or float): Another 'pointCart3D'
				object, a list/tuple with (at least) 2 values, or a single float
		"""
		
		if type(self) == type(other):
			return pointCart2D([self.x / other.x, self.y / other.y])
		elif (type(other) == list) or (type(other) == tuple):
			return pointCart2D([self.x / other[0], self.y / other[1]])
		elif numpy.isreal(other):
			return pointCart2D([self.x / other, self.y / other])
		else:
			raise TypeError("Can't divide '" + str(other) + "' and '" + str(self) + "'")

	def __truediv__(self, other):
		r"""Division overloader (multiple 'type' support)

		This method overloads the '/' operator and allows for the coordinates of
		a 'pointCart2D' object to be divided with either those of another object
		of the same type or with a list, a tuple, or even with a single float

		Parameters:
			other (pointCart2D, list, tuple, or float): Another 'pointCart3D'
				object, a list/tuple with (at least) 2 values, or a single float
		"""

		if type(self) == type(other):
			return pointCart2D([self.x / other.x, self.y / other.y])
		elif (type(other) == list) or (type(other) == tuple):
			return pointCart2D([self.x / other[0], self.y / other[1]])
		elif numpy.isreal(other):
			return pointCart2D([self.x / other, self.y / other])
		else:
			raise TypeError("Can't divide '" + str(other) + "' and '" + str(self) + "'")

	def __floordiv__(self, other):
		r"""Division overloader (multiple 'type' support)

		This method overloads the '/' operator and allows for the coordinates of
		a 'pointCart2D' object to be divided with either those of another object
		of the same type or with a list, a tuple, or even with a single float

		Parameters:
			other (pointCart2D, list, tuple, or float): Another 'pointCart3D'
				object, a list/tuple with (at least) 2 values, or a single float
		"""

		if type(self) == type(other):
			return pointCart2D([self.x // other.x, self.y // other.y])
		elif (type(other) == list) or (type(other) == tuple):
			return pointCart2D([self.x // other[0], self.y // other[1]])
		elif numpy.isreal(other):
			return pointCart2D([self.x // other, self.y // other])
		else:
			raise TypeError("Can't divide '" + str(other) + "' and '" + str(self) + "'")

	def __abs__(self):
		r"""Returns the mangitude of the point as if it was a vector
		
		This method overloads the 'abs' function and calculates the magnitude of
		the 'pointCart2D' as if it was representing a vector. The returned
		result if the square root of the sum of squares of 'x' and 'y'
		"""
		
		return numpy.sqrt(self.x ** 2  +  self.y ** 2)

	@staticmethod
	def calcMidPoint(pointA, pointB):
		r"""Returns the midpoint between two points

		This method calculates the coordinates of the midpoint between two
		'pointCart2D' objects and returns a new 'pointCart2D' point with those
		coordinates

		Parameters:
			pointA (pointCart2D): A 'pointCart2D' object of the first point
			pointB (pointCart2D): A 'pointCart2D' object of the second point

		Returns:
			A 'pointCart2D' object representing the midpoint
		"""

		return pointCart2D([pointA.x + (pointB.x-pointA.x)/2.0,
		                    pointA.y + (pointB.y-pointA.y)/2.0])

	@staticmethod
	def calcDistanceSqrd(pointA, pointB):
		r"""Calculates the squared distance between two points
		
		This method calculates and returns the square of the Eucledian distance
		between two 'pointCart2D' objects
		
		Parameters:
			pointA (pointCart2D): A 'pointCart2D' object of the first point
			pointB (pointCart2D): A 'pointCart2D' object of the second point
		
		Returns:
			A float denoting the eucledian distance between the two points
		"""
		
		p = pointB - pointA
		return (p.x ** 2  +  p.y ** 2)
		
	@staticmethod
	def calcDistance(pointA, pointB):
		r"""Calculates the distance between two points
		
		This method calculates and returns the Eucledian distance between two
		'pointCart2D' objects
		
		Parameters:
			pointA (pointCart2D): A 'pointCart2D' object of the first point
			pointB (pointCart2D): A 'pointCart2D' object of the second point
		
		Returns:
			A float denoting the eucledian distance between the two points
		"""
		return numpy.sqrt(pointCart2D.calcDistanceSqrd(pointA, pointB))
	
	def toList(self):
		r"""Converts a 'pointCart2D' object into a 'list'
		
		This method creates and returns a 'list' object from the reference
		'pointCart2D' object

		Returns:
			A 'list' object with the 'pointCart' object's 'x', and 'y'
			attributes as entries
		"""
		
		#return a list with the 'pointCart2D' coordinates
		return [self.x, self.y]
	
	def toTuple(self):
		r"""Converts a 'pointCart2D' object into a 'tuple'
		
		This method creates and returns a 'tuple' object from the reference
		'pointCart2D' object

		Returns:
			A 'tuple' object with the 'pointCart' object's 'x', and 'y'
			attributes as entries
		"""
		
		#return a 'tuple' with the 'pointCart2D' coordinates
		return (self.x, self.y)