#!/usr/bin/env python

from ._common import IACBase

class IdempotentAccessor(IACBase):
    """The IdempotentAccessor base class is an idempotent store for values.

    This class acts like a dictionary. When a key is referenced, the
    IdempotentAccessor will check for the key in it's current state,
    optionally check that the value for the key is still valid, and
    return the value if it exists. If the value for the key is
    nonexistent or invalid, the IdempotentAccessor will attempt to
    update the value.

    The objects referenced by the accessor are anonymous and
    idempotent. They are anonymous in that you reference the method of
    accessing to get the stored value, not the value itself. This is
    especially useful when it is irrelevant to reference a specific
    object, but important to reference an object of a type tied to a
    specific user.
    
    The property of idempotence comes from the dependency tree that is
    transparently generated as one writes the accessors. By
    referencing objects from the accessor as dependencies of other
    objects the accessor will automatically resolve these
    dependencies. As a result a tester does not need to place the
    system in a state to access an object, but simply requests the
    object and the accessor establishes and maintains that state. 

    The primary use case for this is in web service pen
    testing. Testing some service may require several unique objects
    to exist, which all have to be referenced together. The actual
    values of those references may be irrelevant for some testing. A
    hacker wants to focus on the important areas, letting the system
    maintain everything else. A IdempotentAccessor does this by
    allowing you to set up chained dependencies and automatically
    resolving them.

    To use a IdempotentAccessor, subclass it. Create get_<key>
    functions that return the values for keys. This is illustrated by
    the simple_demo.py in the demo directory:

    from ilwrathi import IdempotentAccessor

     class myIdempotentAccessor(IdempotentAccessor):

     def get_spam(self):
         print "execing spam"
         return "spam"

     def get_eggs(self):
         print "execing eggs"
         return "eggs"

     def get_spamandeggs(self):
         print "execing baz"
         return "spam and eggs relies on %(spam)s and %(eggs)s" % self

     And here's how it works:

     In [1]: myiac = myIdempotentAccessor("myIdempotentAccessor")

     In [2]: myiac
     Out[2]: <myIdempotentAccessor 'myiac': {}>

     In [3]: myiac["spamandeggs"]
     execing baz
     execing spam
     execing eggs
     Out[3]: 'spamandeggs relies on spam and eggs'

     In [4]: myiac
     Out[4]: <myIdempotentAccessor 'myiac': {'eggs': 'eggs', 'spamandeggs': 'baz relies on spam and eggs', 'spam': 'spam'}>

     In [5]: myiac["eggs"]
     Out[5]: 'eggs'

     In [6]: "as a string it looks like: " + myiac
     Out[6]: 'as a string it looks like: myiac'

    It is also possible to add state assurance and object deletion by
    adding extra methods to the class. The return value of the
    check_<key> method is evaluated as a bool to determine if the
    object is still valid. 

    If an object is no longer valid in the system, the accessor will
    automatically call the get_<key> method again to reestablish the
    system state.

    The del_<key> method can be added to remove the <key> from the
    target system when del(iac[key]) is called. 

    """ 
    #http://eli.thegreenplace.net/2011/08/14/python-metaclasses-by-example/

    def __init__(self, name=None, *args, **kwargs):
        self.name = name

    def __getitem__(self, key):
        """x.__getitem__(y) <==> x[y]
        
        If value is in x._cur_values and there is a validation
        function, validates the value and returns value assocated with
        y. If there is no validation function simply returns value
        assocated with y. If there is no value, performs x.get_<y>()
        and populates the x._cur_values cache.

        Be careful of infinite recursion.
        """
        if key in self._cur_values:
            value = self._cur_values[key]
            if not getattr(self, "check_" + key, lambda val:True)(value):
                return self._get_and_update_entry(key)
            return value
        else:
            try:
                return self._get_and_update_entry(key)
            except AttributeError:
                raise KeyError(key)

    def keys(self):
        """D.keys() -> list of D's keys"""
        return self._keys


    def new(self, key):
        """Performs a similar function to x.__getitem__(y) without caching"""
        try:
            val =  getattr(self,"get_" + key)()
            self.history.append(val)
            return val
        except KeyError:
            raise KeyError(key)

    def _get_and_update_entry(self, key):
        """x._get_and_update_entry(y) <==> del(x[y]) then x[y]
        
        Archives old values and gets a new copy of `key`.
        """
        self._archive_vals()
        val = getattr(self,"get_" + key)()
        self._cur_values[key] = val
        return val

    def __setitem__(self, key, value):
        """x.__setitem__(i, y) <==> x[i]=y or x.set_<i>(y)

        Archive values in history. If x.set_<i> exists set
        x[i]=x.set_<i>(y). If not, simply set x[i]=y.
        """
        if not key in self._keys:
            raise KeyError(key)
        self._archive_vals()
        self._cur_values[key] = getattr(self, "set_" + key, 
                                        lambda v: v)(value)

    def __delitem__(self, key):
        """x.__delitem__(y) <==> del(x[y])
        
        If x.del_<y> exists, x.del_<y>(), then del(x[y]). If not,
        del(x[y]).

        """
        self._archive_vals()
        if not key in self._keys:
            raise KeyError(key)
        getattr(self, "del_" + key, lambda cls: None)()
        del(self._cur_values[key])

    def __str__(self):
        return self.name

    def __setattr__(self, name, value):
        if name.startswith('get_'):
            self._keys.append(name[4:])
            setattr(self.__class__, name, value)
        else:
            self.__dict__[name] = value

    def __delattr__(self, name):
        if name.startswith('get_'):
            self._keys.remove(name[4:])
            delattr(self.__class__, name)
        else:
            del(self.__dict__[name])

    def __iter__(self):
        return self

    def next(self):
        #do something better with this
        self.clear()
        return self

    def __add__(self, other):
        """x.__add__(y) <==> x+y"""
        return self.name + other

    def __radd__(self, other):
        """x.__radd__(y) <==> y+x"""
        return other + self.name
        
    def __repr__(self):
        return "<%s '%s': %s>" % (self.__class__.__name__,
                                  str(self.name),
                                  str(self._cur_values))

    def clear(self):
        self._archive_vals()
        self._cur_values = {}

    def _archive_vals(self):
        if self._cur_values:
            self.history.append(dict(self._cur_values))
