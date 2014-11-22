import math 

"""
    Provides a module for packing and unpacking integer representations
    of binary flags. 

    `code` does the packing: it takes a list of integers, or "flags", 
    and returns a unique code, a single integer. `flags` is the inverse
    function, taking a code and unpacking it into flags. 

    All the methods take an `index_base` param, which should be the 
    base index for flags passed in, or unpacked from a code, i.e. 
    0 for a zero-based index or 1 for a one-based index. """
    

""" Returns the nth member of the y=2^(`n`-`index_base`) sequence. """
def _seq(n, index_base=0):
    return 2 ** (n-index_base)


""" Retrieves the flag, or index, of the highest member of `_seq`
    contained within `code`. """
def _highest_flag(code, index_base=0):
    return int(math.log(code, 2)) + index_base


""" Returns the flags uniquely corresponding to `code`. """
def flags(code, index_base=0):
    if code > 0:
        highest = _highest_flag(code, index_base)
        return flags((code - _seq(highest, index_base)), index_base) + [highest]
    return []


""" Returns the code uniquely corresponding to `flags`. """
def code(flags, index_base=0):
    return sum([_seq(f, index_base) for f in flags])

    