#!/usr/bin/env python

def decompose(total, mixture, stack=[], result=[]):
    """
    """
    #NOTE: This is a sort of Beta-expansion.
    if not mixture:
        if not total:
            result.append(list(stack))
        return
    #if

    for multiplier in range(total // mixture[0], -1, -1):
        stack.append(multiplier)
        decompose(total - mixture[0] * multiplier, mixture[1:], stack=stack,
            result=result)
        stack.pop()
    #for
    return result
#decompose

def main():
    """
    """
    mixture = [18, 7, 5, 2, 1]
    result = decompose(20, mixture)

    print mixture
    print 
    for line in result:
        print line
#main

if __name__ == "__main__":
    main()
