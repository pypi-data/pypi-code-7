from __future__ import unicode_literals
import logging
import collections


logger = logging.getLogger(__file__)


class Error(object):
    """
    Sentinal value for knowing when a callable raised an error.
    """
    pass

error = Error()


COMPLETENESS_THRESHOLD = 75


class Registry(object):
    error_messages = {
        # Logging messages (use %s formatting)
        'callback_error': (
            "Error while gathering data with call signature %s, func:%s, "
            "exc: %s"
        ),
        'unregistered_keys': (
            "Unexpected keys returned from %s for call signature %s. "
            "Expected `%s`.  Got extra `%s`"
        ),
        'key_not_returned': (
            "Function `%s` for call signature %s did not return the key "
            "`%s`.  Returned: `%s`"
        ),
        'too_much_missing_data': (
            "Data for call signature %s was only %s% complete"
        ),
        # Exception Messages (use {} formatting)
        'key_already_registered': "The following key(s) are already registered:",
        'function_already_registered': ("The function {0} has already been "
                                        "registered to the keys `{1}`"),
    }

    def __init__(self):
        self.functions = {}
        self.keys_for_function = collections.defaultdict(list)

    def register(self, *keys):
        """
        Decorator for registering a function.

        Each function must:
            - Have similar or compatable call signatures.
            - Return a mapping of the keys it was registered with and
              associated values.
            - In the case it is registered with a single key, it may return
              only that value (as long as that value is not a mapping).

        Usage:

            >>> registry = Registry()
            >>> @registry.register('key_1', 'key_2')
            ... def callback(value):
            ...     return {'key_1': ..., 'key_2': ...}
            >>> registry(value)
            {'key_1': ..., 'key_2': ...}
        """
        intersection = set(self.functions.keys()).intersection(keys)
        if intersection:
            msg = self.error_messages['key_already_registered']
            for key in intersection:
                msg += "\n> {0}: {1}".format(key, repr(self.functions[key]))
            raise ValueError(msg)

        def register_decorator(func):
            if func in self.keys_for_function:
                raise ValueError(
                    self.error_messages['function_already_registered'].format(
                        func, self.keys_for_function[func],
                    ),
                )
            for key in keys:
                self.functions[key] = func
            self.keys_for_function[func].extend(keys)
            return func

        return register_decorator

    def get_value_from_result(self, func, key, result, args, kwargs):
        """
        Get the desired value from the function result.  In addition, log
        whether the function returned *extra* keys.
        """
        if isinstance(result, collections.Mapping):
            extras = set(result.keys()).difference(self.keys_for_function[func])
            if extras:
                logger.error(
                    self.error_messages['unregistered_keys'],
                    repr(func), repr((args, kwargs)),
                    self.keys_for_function[func], extras,
                )
            try:
                value = result[key]
            except KeyError:
                logger.error(
                    self.error_messages['key_not_returned'],
                    repr(func), repr((args, kwargs)), key, result,
                )
        else:
            value = result
        return value

    def check_data_completeness(self, data, args, kwargs):
        """
        Ensure that the final data gathered for a given value is above
        COMPLETENESS_THRESHOLD percent complete.  If it isn't something is
        probably wrong and we should log it.
        """
        completeness = len(data) * 100 / len(self.functions)
        if completeness < COMPLETENESS_THRESHOLD:
            logger.error(
                self.error_messages['too_much_missing_data'],
                repr((args, kwargs)), completeness,
            )

    def __call__(self, *args, **kwargs):
        """
        Gather all of the callback data from the registered callbacks.
        """
        data = {}
        cache = {}

        for key, func in self.functions.items():
            if func not in cache:
                try:
                    cache[func] = func(*args, **kwargs)
                except Exception as e:
                    cache[func] = error
                    logger.error(
                        self.error_messages['callback_error'],
                        repr((args, kwargs)), repr(func), repr(e),
                    )
                    continue

            result = cache[func]

            if result is error:
                continue

            data[key] = self.get_value_from_result(
                func, key, result, args=args, kwargs=kwargs,
            )

        self.check_data_completeness(data, args=args, kwargs=kwargs)
        return data
