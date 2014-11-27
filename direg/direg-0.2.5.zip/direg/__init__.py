# -*- coding: utf-8 -*-
"""
direg Overview
**************

direg lets you maintain arbitrary registry data (in the form of python dictionaries that can be "merged" in a logical
way (think: global config -vs- user config). With a small amount of work, it is possible to replace hardcoded
values with easily-maintainable and flexible registry entries.

Suppose we have a file at ``/my/path/registry.py`` with the following contents.

.. code-block:: python

    data = {
        'one.Foo.meth.somevar': 26804,
        'one.Foo.somevar': 24742,
        'one.myfunc.somevar': 16834,
        'one.outer.inner.somevar': 7678,
    }


Then, in some module ``one``, we can do the following:

``one.py``

.. code-block:: python

    from direg import get_value, registries
    # Load the registry with the above data. Note that this could take place in another module and could include an
    # arbitrary number of registry files.
    registries.append('/my/path/registry.py')

    class Foo:
        somevar = get_value('somevar')  # will be 24742
        def meth(self):
            return get_value('somevar')

    f = Foo()
    f.meth()  # will return 26804
    f.somevar  # 24742
    Foo.somevar  # also 24742

    def myfunc():
        somevar = get_value('somevar')
        return somevar

    myfunc()  # will be 16834
"""

from main import *
