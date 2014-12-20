import re

def atoi(text):
    '''transform [text] into an integer if it is a number'''
    return int(text) if text.isdigit() else text

def naturalKeys(text):
    return [ atoi(c) for c in re.split('(\d+)', text) ]


def naturalSorting(l):
    '''
    sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    
    >>> alist = [      \
        "something1",  \
        "something12", \
        "something17", \
        "something2",  \
        "something25", \
        "something29"]
    
    >>> print naturalSorting(alist)
    ['something1', 'something2', 'something12', 'something17', 'something25', 'something29']
    '''
    l.sort(key=naturalKeys)
    return l


if __name__ == "__main__":
    import doctest
    doctest.testmod()
