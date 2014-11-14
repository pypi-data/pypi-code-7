"""
A collection of functions for use in projects using GameBaker.
All angles are in degrees, anticlockwise from the right (the 3 o'clock position on a clock face).
The origin is at the top left.
Unlike in maths (but as is common for computer graphics), the y axis goes from top to bottom.

Included in this module, but not separately documented are the following functions:

    - sin
    - cos
    - tan
    - asin
    - acos
    - atan
    
These function exactly like their counterparts in ``math`` in the standard library, but work with degrees rather than radians.
"""

import math

def send_degrees(function):
    """
    Wraps a function with one argument by calling ``math.radians`` on that argument before it is called.
    """
    return (lambda x: function(math.radians(x)))
    
def recieve_degrees(function):
    """
    Wraps a function with one argument by calling ``math.degrees`` on the result.
    """
    return (lambda x: math.degrees(function(x)))
    
sin = send_degrees(math.sin)
cos = send_degrees(math.cos)
tan = send_degrees(math.tan)

asin = recieve_degrees(math.asin)
acos = recieve_degrees(math.acos)
atan = recieve_degrees(math.atan)

def distance(x1, y1, x2, y2):
    """
    Calculate the distance between two points.
    """
    return math.sqrt((x1-x2)**2 + (y1-y2)**2)
    
def angle(x1, y1, x2, y2):
    """
    Calculate the angle between two points.
    """
    x_distance = abs(x1-x2)
    y_distance = abs(y1-y2)
    if x_distance == 0:
        angle = 90
    else:
        angle = atan(y_distance/x_distance)
    if x1 <= x2 and y1 >= y2:
        return angle
    elif x1 >= x2 and y1 >= y2:
        return 180 - angle
    elif x1 >= x2 and y1 <= y2:
        return 180 + angle
    elif x1 <= x2 and y1 <= y2:
        return 360 - angle
    else:
        raise ValueError("Angle between ({}, {}) and ({}, {}) could not be calculated".format(x1, y1, x2, y2))
        
def point_along_angle(x, y, angle, distance):
    """
    Return a point at a certain distance and angle from another point.
    """
    x_difference = distance * cos(angle)
    y_difference = -1 * distance * sin(angle)
    
    return (x + x_difference, y + y_difference)
    
def xy_diff(x1, y1, x2, y2):
    """
    Return ``(x2 - x1, y2 - y1)``
    """
    return (x2 - x1, y2 - y1)
    
def multiply_vector(scalar, vector):
    """
    Returns ``scalar * vector``, where ``vector`` is a tuple and scalar a number.
    """
    return tuple(scalar*x for x in vector)
    