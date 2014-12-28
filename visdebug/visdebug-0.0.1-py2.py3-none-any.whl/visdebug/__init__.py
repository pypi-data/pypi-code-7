import colorama
class VisdebugException(Exception):
    pass

def sarr(arr, loc):
    """Some pretty printing"""
    if not all(map(lambda x: x < len(arr), loc)):
        raise VisdebugException("You have an index that's larger then the length of the array")
    parts = []
    for i, el in enumerate(arr):
        if i in loc:
            parts.append(colorama.Back.WHITE + str(el) + colorama.Back.RESET)
        else:
            parts.append(str(el))
    return '[{}]'.format(', '.join(parts))


def parr(arr, loc):
    print(sarr(arr, loc))
