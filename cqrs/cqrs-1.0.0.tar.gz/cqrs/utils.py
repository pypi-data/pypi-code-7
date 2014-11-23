import importlib


def import_string(dotted_path):
    """
    Import a dotted module path and return the attribute/class
    designated by the last name in the path. Raise :exc:`ImportError`
    if the import failed.

    Args:
        dotted_path: a string containing the fully-qualified path
            to an attribute in a Python module.

    Returns:
        object: the attribute specified by `dotted_path`.
    """
    dotted_path = str(dotted_path)
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except ValueError:
        msg = "{0} doesn't look like a module path".format(dotted_path)
        raise ImportError(msg)

    module = importlib.import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError:
        msg = 'Module "{0}" does not define a "{1}" attribute/class'.format(
            dotted_path, class_name)
        raise ImportError(msg)
