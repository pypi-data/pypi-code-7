from importlib import import_module
from pprint import pformat

from datetime import datetime
from floraconcierge import errors


def module_name_from_class(cls):
    class_name = ('floraconcierge.mapping.%s' % cls.replace("_", '.').lower()).split('.')
    module, name = ".".join(class_name[:-1]), class_name[-1].capitalize()

    return module, name


def from_dict(obj):
    """
    Creates floraconcierge api result object instance
    @param obj: dict
    @return: Object
    """
    if '_className' in obj and obj['_className']:
        module, name = module_name_from_class(obj['_className'])

        try:
            m = import_module(module)
            cls = getattr(m, name)
        except (ImportError, AttributeError):
            errtpl = '%s.%s for api "%s" mapping not found'
            raise errors.ModelMappingNotFoundError(errtpl % (module, name, obj['_className']))

        return cls(**obj)

    return Object(**obj)


class Object(object):
    def __init__(self, *args, **kwargs):
        super(Object, self).__init__()

        if '_className' in kwargs:
            del kwargs['_className']

        for k, v in kwargs.iteritems():
            try:
                v = int(v)
            except (ValueError, TypeError):
                try:
                    v = float(v)
                except (ValueError, TypeError):
                    pass

            kwargs[k] = v

        self.__dict__.update(kwargs)

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, pformat(self.__dict__))

    def datetime(self, unixtime):
        return datetime.fromtimestamp(int(unixtime))
