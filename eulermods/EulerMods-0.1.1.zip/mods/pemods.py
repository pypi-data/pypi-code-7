"""
Collection of Python modules to aid in solving Project Euler problems
Developed by Ryan Cox
Licensed under the MIT License

The MIT License (MIT)

Copyright (c) 2014 Ryan Cox

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


def palindrome(num):
    # Check if a string or number is a palindrome
    # Last updated 4.12.14
    return str(num) == str(num)[::-1]
    
def prime_check(x):
    # Check if a number is prime
    # Last updated 4.12.14
    for i in range(2, x, 1):
        if x%i == 0:
            return False
    return True

def range_sum(start, stop, step):
    # Find the sum of a range
    # Last updated 4.12.14
    return sum(range(start, stop, step))

