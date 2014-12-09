
from dk.collections import pset


class css(pset):
    def __init__(self, **attrs):
        super(css, self).__init__()
        for key, val in attrs.items():
            self[key.replace('_', '-')] = val
        
    def __setattr__(self, key, val):
        super(css, self).__setattr__(key.replace('_', '-'), val)
    
    def __str__(self):
        return ';'.join('%s:%s' % (k,v) for (k,v) in self.items())

    __repr__ = __str__


def _test():
    """
       >>> x = css(color='red', background='blue')
       >>> x
       color:red;background:blue
       >>> x.border = 'none'
       >>> y = css(background='blue', color='red')
       >>> y.border = 'none'
       >>> x == y
       True
       >>> a = css()
        >>> a['font-weight'] = 'bold'
        >>> a
        font-weight:bold
        >>> a.text_align = 'right'
        >>> a
        font-weight:bold;text-align:right
    """
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
