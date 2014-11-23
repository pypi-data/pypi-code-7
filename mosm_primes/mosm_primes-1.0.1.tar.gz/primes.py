"""
Simple Check of prime numbers, with the empiric indian math method.
"""


import math

"""
This function requires a integer number and 
return True if is prime or False if not
"""
def isPrime(number):
	global firstDivisor
	limit = range(2,int(math.sqrt(number))+1)
	for eachDivisor in limit:
		if number % eachDivisor == 0:
			firstDivisor = eachDivisor
			return False
	return True

"""
This function requires a integer number and return
a list of prime components of this number
"""
def primeComponents(number):
	pComponents = set([1])
	while(True):
		if(isPrime(number) == False):
			pComponents.add(firstDivisor)
			number = number // firstDivisor
		else:
			pComponents.add(number)
			return sorted(list(pComponents))

print(primeComponents(11))


