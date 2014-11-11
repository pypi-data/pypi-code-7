# -*- coding: utf-8 -*-

"""
Python reflection tools.
"""

from b3j0f.utils.version import PY2
from b3j0f.utils.iterable import ensureiterable

from inspect import isclass, isroutine, ismethod, getmodule

try:
    from types import NoneType
except ImportError:
    NoneType = type(None)

__all__ = ['base_elts', 'find_embedding', 'is_inherited']


def base_elts(elt, cls=None, depth=None):
    """
    Get bases elements of the input elt.

    - If elt is an instance, get class and all base classes.
    - If elt is a method, get all base methods.
    - If elt is a class, get all base classes.
    - In other case, get an empty list.

    :param elt: supposed inherited elt.
    :param cls: cls from where find attributes equal to elt. If None,
        it is found as much as possible. Required in python3 for function
        classes.
    :type cls: type or list
    :param int depth: search depth. If None (default), depth is maximal.
    :return: elt bases elements. if elt has not base elements, result is empty.
    :rtype: list
    """

    result = []

    elt_name = getattr(elt, '__name__', None)

    if elt_name is not None:

        cls = [] if cls is None else ensureiterable(cls)

        elt_is_class = False

        # if cls is None and elt is routine, it is possible to find the cls
        if not cls and isroutine(elt):

            if hasattr(elt, '__self__'):  # from the instance

                instance = elt.__self__  # get instance

                if instance is None and PY2:  # get base im_class if PY2
                    cls = list(elt.im_class.__bases__)

                else:  # use instance class
                    cls = [instance.__class__]

        # cls is elt if elt is a class
        elif isclass(elt):
            elt_is_class = True
            cls = list(elt.__bases__)

        if cls:  # if cls is not empty, find all base classes

            index_of_found_classes = 0  # get last visited class index
            visited_classes = set(cls)  # cache for visited classes
            len_classes = len(cls)

            if depth is None:  # if depth is None, get maximal value
                depth = -1  # set negative value

            while depth != 0 and index_of_found_classes != len_classes:
                len_classes = len(cls)

                for index in range(index_of_found_classes, len_classes):
                    _cls = cls[index]

                    for base_cls in _cls.__bases__:
                        if base_cls in visited_classes:
                            continue

                        else:
                            visited_classes.add(base_cls)
                            cls.append(base_cls)
                index_of_found_classes = len_classes
                depth -= 1

            if elt_is_class:
                # if cls is elt, result is classes minus first class
                result = cls

            elif isroutine(elt):

                # get an elt to compare with found element
                elt_to_compare = elt.__func__ if ismethod(elt) else elt

                for _cls in cls:  # for all classes
                    # get possible base elt
                    b_elt = getattr(_cls, elt_name, None)

                    if b_elt is not None:
                        # compare funcs
                        bec = b_elt.__func__ if ismethod(b_elt) else b_elt
                        # if matching, add to result
                        if bec is elt_to_compare:
                            result.append(b_elt)

    return result


def is_inherited(elt, cls=None):
    """
    True iif elt is inherited.
    """

    return base_elts(elt, cls=cls, depth=1)


def find_embedding(elt, embedding=None):
    """
    Try to get elt embedding elements.

    :param embedding: embedding element. Must be have a module.

    :return: a list of [module [,class]*] embedding elements which define elt:
    """

    result = []  # result is empty in the worst case

    # start to get module
    module = getmodule(elt)

    if module is not None:  # if module exists

        visited = set()  # cache to avoid to visit twice same element

        if embedding is None:
            embedding = module

        # list of compounds elements which construct the path to elt
        compounds = [embedding]

        while compounds:  # while compounds elements exist
            # get last compound
            last_embedding = compounds[-1]
            # stop to iterate on compounds when last embedding is elt
            if last_embedding == elt:
                result = compounds  # result is compounds
                break

            else:
                # search among embedded elements
                for name in dir(last_embedding):
                    # get embedded element
                    embedded = getattr(last_embedding, name)

                    try:  # check if embedded has already been visited
                        if embedded not in visited:
                            visited.add(embedded)  # set it as visited

                        else:
                            continue

                    except TypeError:
                        pass

                    else:

                        try:  # get embedded module
                            embedded_module = getmodule(embedded)
                        except Exception:
                            pass
                        else:
                            # and compare it with elt module
                            if embedded_module is module:
                                # add embedded to compounds
                                compounds.append(embedded)
                                # end the second loop
                                break

                else:
                    # remove last element if no coumpound element is found
                    compounds.pop(-1)

    return result
