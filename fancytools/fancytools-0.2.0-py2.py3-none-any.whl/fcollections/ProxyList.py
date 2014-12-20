
class _CallList(list):
    def __call__(self, *arg, **kwarg):
        return [x(*arg, **kwarg) for x in self]

def _pass(*args, **kwargs):
    pass

class ProxyList(list):
    '''
    forwards an attribute/method given to this instance
    to its list-entries
    
    create a list
    >>> a = ProxyList(('aa',11,'cc'))
    
    find 'a' in the list
    because 'find' is not a method of this instance
    all list-entries will be given this method
    
    
    >>> print a.find('a')
    [0, None, -1]
    
    ... this returns a list saying that...
    [0,...    --> 'a' is in the first position of the first entry
    ..., None --> there is no fitting method for the second entry
    ... ,-1 ] --> 'a' is not found in the last entry
    
    
    show indices of list entries that are of type string
    
    >>> print a.where('__class__',str)
    [0, 2]
    '''
    def __getattr__(self, attr):
        try:
            return list.__getattribute__(self, attr)
        except AttributeError:
            return _CallList( getattr(x, attr, _pass) for x in self )
        


    def where(self, attr, value):
        return [n for n,x in enumerate(self) if getattr(x, attr, _pass) == value]
        #return next((n for n,x in enumerate(self) if getattr(x, attr, _pass) == value), None)


if __name__ == "__main__":
    import doctest
    doctest.testmod()