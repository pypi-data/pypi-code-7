from jaraco.util import dictlib

class Environment(dict, dictlib.ItemsAsAttributes):
    """A namespace with a set of defaults.

    Our items can also be accessed as attributes.  This is limited to read-only
    access; generalized attribute mutation/deletion DOES NOT WORK.

    Eggmonster applications may use an instance of this class as a
    global configuration namespace.
    """

    def __init__(self, *args, **kwargs):
        super(Environment, self).__init__(*args, **kwargs)
        self._locals = dict()
        self._defaults = dict()

    def __delitem__(self, key):
        """Delete self[key].

        This method deletes local values only; it does not delete from defaults.
        """
        del self._locals[key]
        self._regenerate()

    def __setitem__(self, key, value):
        """Set self[key] = value.

        This method sets local values only; it does not assign into defaults.
        """
        self._locals.__setitem__(key, value)
        self._regenerate()

    def _regenerate(self):
        """Private method to regenerate self after mutation.
        """
        super(Environment, self).clear()
        super(Environment, self).update(self._defaults)
        super(Environment, self).update(self._locals)

    def as_obscured_dict(self, keys_to_obscure=['password']):
        """Return ourself as a dict, suitable for public viewing.

        Items whose key is in <keys_to_obscure> have their value obscured
        to thwart data leakage.
        """
        def _hide_obscured_names(items, keys_to_obscure):
            """Recursively copy items into a dict, obscuring the named items.
            """
            result = {}
            for key, value in items:
                if isinstance(value, dict):
                    result[key] = _hide_obscured_names(value.items(), keys_to_obscure)
                elif key in keys_to_obscure:
                    result[key] = '********'
                else:
                    result[key] = value
            return result

        return _hide_obscured_names(self.items(), keys_to_obscure)

    def clear_defaults(self):
        self._defaults.clear()
        self._regenerate()

    def clear_locals(self):
        self._locals.clear()
        self._regenerate()

    clear = clear_locals

    def update_defaults(self, *args, **kwargs):
        self._defaults.update(*args, **kwargs)
        self._regenerate()

    def update_locals(self, *args, **kwargs):
        self._locals.update(*args, **kwargs)
        self._regenerate()

    update = update_locals
