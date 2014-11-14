from doubles.exceptions import UnallowedMethodCallError
from doubles.proxy_property import ProxyProperty

double_name = lambda name: 'double_of_' + name


class ProxyMethod(object):
    """
    The object that replaces the real value of a doubled method. Responsible for hijacking the
    target object, finding matching expectations and returning their values when called, and
    restoring the original value to the hijacked object during teardown.
    """

    def __init__(self, target, method_name, find_expectation):
        """
        :param Target target: The object to be hijacked.
        :param str method_name: The name of the method to replace.
        :param function find_expectation: A function to call to look for expectations that match
             any provided arguments.
        """

        self._target = target
        self._method_name = method_name
        self._find_expectation = find_expectation
        self._attr = target.attrs[method_name]

        self._capture_original_method()
        self._hijack_target()

    def __call__(self, *args, **kwargs):
        """
        The actual invocation of the doubled method.

        :param tuple args: The arguments the doubled method was called with.
        :param dict kwargs: The keyword arguments the doubled method was called with.
        :return: The return value the doubled method was declared to return.
        :rtype: object
        :raise: ``UnallowedMethodCallError`` if no matching doubles were found.
        """

        expectation = self._find_expectation(args, kwargs)

        if not expectation:
            self._raise_exception(args, kwargs)

        expectation.verify_arguments(args, kwargs)

        return expectation.return_value(*args, **kwargs)

    def __get__(self, instance, owner):
        """
        Implements the descriptor protocol to allow doubled properties to behave as properties.

        :return: The return value of any matching double in the case of a property, self otherwise.
        :rtype: object, ProxyMethod
        """

        if self._attr.kind == 'property':
            return self.__call__()

        return self

    def restore_original_method(self):
        """Replaces the proxy method on the target object with its original value."""

        if self._target.is_class():
            setattr(self._target.obj, self._method_name, self._original_method)
        elif self._attr.kind == 'property':
            setattr(self._target.obj.__class__, self._method_name, self._original_method)
            del self._target.obj.__dict__[double_name(self._method_name)]
        else:
            # TODO: Could there ever have been a value here that needs to be restored?
            del self._target.obj.__dict__[self._method_name]

        if self._method_name in ['__call__', '__enter__', '__exit__']:
            self._target.restore_attr(self._method_name)

    def _capture_original_method(self):
        """Saves a reference to the original value of the method to be doubled."""

        self._original_method = self._attr.object

    def _hijack_target(self):
        """Replaces the target method on the target object with the proxy method."""

        if self._target.is_class():
            setattr(self._target.obj, self._method_name, self)
        elif self._attr.kind == 'property':
            proxy_property = ProxyProperty(
                double_name(self._method_name),
                self._original_method,
            )
            setattr(self._target.obj.__class__, self._method_name, proxy_property)
            self._target.obj.__dict__[double_name(self._method_name)] = self
        else:
            self._target.obj.__dict__[self._method_name] = self

        if self._method_name in ['__call__', '__enter__', '__exit__']:
            self._target.hijack_attr(self._method_name)

    def _raise_exception(self, args, kwargs):
        """
        Raises an ``UnallowedMethodCallError`` with a useful message.

        :raise: ``UnallowedMethodCallError``
        """

        error_message = (
            "Received unexpected call to '{}' on {!r}.  The supplied arguments "
            "(args={}, kwargs={}) do not match any available allowances."
        )
        raise UnallowedMethodCallError(
            error_message.format(
                self._method_name,
                self._target.obj,
                args,
                kwargs
            )
        )
