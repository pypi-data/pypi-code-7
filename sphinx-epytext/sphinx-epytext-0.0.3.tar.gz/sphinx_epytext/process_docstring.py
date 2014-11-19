# -*- coding: utf-8 -*-
"""Process docstrings."""

import re

FIELDS = [
    'param',
    'keyword',
    'kwarg',
    'type',
    'returns',
    'return',
    'rtype',
    'raises',
    'exception',
    'see',
    'note',
    # not tested
    'attention',
    'bug',
    'warning',
    'version',
    'todo',
    'deprecated',
    'since',
    'status',
    'change',
    'permission',
    'requires',
    'precondition',
    'postcondition',
    'invariant',
    'author',
    'organization',
    'copyright',
    'license',
    'contact',
    'summary',
]

# Not supported yet: 'group', 'sort'


def process_docstring(app, what, name, obj, options, lines):
    """Process the docstring for a given python object.

    Called when autodoc has read and processed a docstring. `lines` is a list
    of docstring lines that `_process_docstring` modifies in place to change
    what Sphinx outputs.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        Application object representing the Sphinx process.
    what : str
        A string specifying the type of the object to which the docstring
        belongs. Valid values: "module", "class", "exception", "function",
        "method", "attribute".
    name : str
        The fully qualified name of the object.
    obj : module, class, exception, function, method, or attribute
        The object to which the docstring belongs.
    options : sphinx.ext.autodoc.Options
        The options given to the directive: an object with attributes
        inherited_members, undoc_members, show_inheritance and noindex that
        are True if the flag option of same name was given to the auto
        directive.
    lines : list of str
        The lines of the docstring, see above.

        .. note:: `lines` is modified *in place*

    """
    result = [re.sub(r'U\{([^}]*)\}', r'\1',
                     re.sub(r'(L|C)\{([^}]*)\}', r':py:obj:`\2`',
                            re.sub(r'@(' + '|'.join(FIELDS) + r')', r':\1',
                                   l)))
              for l in lines]
    lines[:] = result[:]
