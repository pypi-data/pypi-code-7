"""Mocks for things."""
from collections import deque
patched = []


class CallTracker(object):
    def __init__(self):
        self.mock_calls = deque()
        self.mock_returns = deque()

    def clear(self):
        self.mock_calls.clear()
        self.mock_returns.clear()

    def add_call(self, name, args=None, kwargs=None, retval=None, context=None):
        """Add a call."""
        self.mock_calls.append((name, args, kwargs, retval, context))

    def next_call(self):
        """Remove and return the next call value from the queue."""
        if self.mock_calls:
            return self.mock_calls.popleft()
        return None

    def add_return(self, value):
        """Add a return value to the call queue."""
        self.mock_returns.append(value)

    def next_return(self):
        """Remove and return the next return value from the queue."""
        if self.mock_returns:
            return self.mock_returns.popleft()
        return None


class ToolMock(object):
    """Create a mock commandline tool."""

    def __init__(self, *args, **kwargs):
        self._mock = CallTracker()
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        args = self.args + args
        kwargs = self.kwargs.copy()
        kwargs.update(kwargs)
        tool = self.__class__(*args, **kwargs)
        tool._mock = self._mock
        return tool

    def _call(self, name, *args, **kwargs):
        context = {'args': self.args, 'kwargs': self.kwargs}
        retval = self._mock.next_return()
        self._mock.add_call(name, args, kwargs, retval, context)
        if isinstance(retval, Exception):
            raise retval
        return retval

    def _clear(self):
        self._mock._clear()

    def call(self):
        return self._call('call')

    def quiet(self, stderr=None):
        return self._call('quiet', stderr=stderr)

    def capture(self, stderr=None):
        return self._call('capture', stderr=stderr)


class BestVersionMock(object):
    """Mock ```version.get_best_version```."""
    def __init__(self, version):
        self.version = version

    def __call__(self, container, verify):
        if verify and not self.version.verified:
            return None
        return self.version


class AllVersionsMock(object):
    """Mock ```version.get_all_versions```."""
    def __init__(self, versions):
        self.versions = versions

    def __call__(self, container):
        return self.versions


def patch(module, name, obj):
    """Replace ``name`` in ``module`` with the provided ``obj``."""
    old = getattr(module, name, None)
    patched.append((module, name, old))
    setattr(module, name, obj)


def unpatch():
    for module, name, obj in reversed(patched):
        setattr(module, name, obj)


def patch_container(best_version=None, all_versions=None):
    """Replace the tool class with our mock."""
    from containerctl import container
    patch(container, 'Tool', ToolMock)

    if all_versions is not None and best_version is None:
        best_version = all_versions[0] if all_versions else None
    if best_version is not None and all_versions is None:
        all_versions = [best_versions]

    if best_version is not None:
        patch(container, 'get_best_version', BestVersionMock(best_version))
    if all_versions is not None:
        patch(container, 'get_all_versions', AllVersionsMock(all_versions))
