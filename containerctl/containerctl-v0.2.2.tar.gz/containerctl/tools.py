"""Simplify repeatable execution of commandline tools."""
import os
import subprocess


class Tool(object):
    """Create a commandline tool."""

    def __init__(self, *args, **kwargs):
        """Create a tool that calls the command provided in arguments. Keyword arguments are passed
        to ``subprocess.Popen``."""
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        """Append arguments to this tool and return a new one. Keyword arguments to Popen may also
        be added or replaced."""
        args = self.args + args
        kwargs = self.kwargs.copy()
        kwargs.update(kwargs)
        return self.__class__(*args, **kwargs)

    def call(self):
        """Call the command. Return the exit code. Raise ``OSError`` on Popen failure."""
        return subprocess.call(self.args, **self.kwargs)

    def quiet(self, stderr=None):
        """Call the command and redirect stdout to /dev/null. If ``stderr`` is ``True`` also
        redirect stderr to /dev/null. Return the exit code. Raise ``OSError`` on Popen failure."""
        with open(os.devnull, 'w') as devnull:
            kwargs = self.kwargs.copy()
            kwargs['stdout'] = devnull
            if stderr:
                kwargs['stderr'] = devnull
            return subprocess.call(self.args, **kwargs)

    def capture(self, stderr=None):
        """Call the command and capture its output. Return the captured stdout, stderr, and exit
        code. By default stderr is not captured and its return value is ``None``. Set ``stderr`` to
        ``True`` to also capture stderr. Raise ``OSError`` on Popen failure."""
        kwargs = self.kwargs.copy()
        kwargs['stdout'] = subprocess.PIPE
        if stderr:
            kwargs['stderr'] = subprocess.PIPE
        proc = subprocess.Popen(self.args, **kwargs)
        stdout, stderr = proc.communicate()
        return stdout, stderr, proc.returncode
