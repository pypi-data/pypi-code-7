from functools import reduce

def sum(n):
    return reduce(lambda x,y:x+y, range(1, n+1))

def factorial(n):
    return reduce(lambda x,y:x*y, range(1, n+1))