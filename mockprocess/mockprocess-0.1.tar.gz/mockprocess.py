import subprocess

_REAL_CHECK_OUTPUT = subprocess.check_output


class MockCheckOutput(object):
    r"""A subprocess.check_output mock

    This is a context manager that will mock out subprocess.check_output and
    behave has you've told it to.  See the following examples, but note that
    the command that you specify is not actually run.

    >>> import subprocess
    >>> import unittest
    >>> class Test(unittest.TestCase):
    ...     def test_simple(self):
    ...         with MockCheckOutput('hello\n'):
    ...             output = subprocess.check_output(['/bin/echo', 'hello'])
    ...         self.assertEqual(output, 'hello\n')
    ...

    If you need to test how you handle errors, you can set an exit code as well.

    >>> import subprocess
    >>> import unittest
    >>> class Test(unittest.TestCase):
    ...     def test_exception(self):
    ...         try:
    ...             with MockCheckOutput('hello\n', exit_code=127):
    ...                 subprocess.check_output(['/bin/false'])
    ...         except subprocess.CalledProcessError as exp:
    ...             pass
    ...         else:
    ...             self.fail('exception was not raised')
    """

    def __init__(self, output, exit_code=0):
        self.output = output
        self.exit_code = exit_code


    def __enter__(self):
        def _mock_check_output(*args, **kwargs):
            if self.exit_code > 0:
                cmd = None

                cmd = kwargs.get('args', None)
                if cmd is None and len(args) > 0:
                    cmd = args[0]

                raise subprocess.CalledProcessError(self.exit_code, cmd, self.output)

            return self.output

        subprocess.check_output = _mock_check_output


    def __exit__(self, typ, value, tb):
        subprocess.check_output = _REAL_CHECK_OUTPUT

