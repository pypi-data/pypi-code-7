"""Retrieve versions from git."""
import os
import pipes
import subprocess
from ..errors import VersionError
from .base import Detector, Version


class GitDetector(Detector):
    """Return git tags and short SHA hash of the HEAD revision (prepended with 'r') as versions."""

    def _valid(self):
        """Return ``True`` if git command exists and the container directory is in a git repo."""
        try:
            with open(os.devnull, 'w') as null:
                subprocess.check_call(['git', 'status'], cwd=self.container.path,
                                      stdout=null, stderr=null)
            return True
        except (subprocess.CalledProcessError, OSError):
            return False

    def _verify(self, tag):
        """Return ``True`` if a tag is signed and verified."""
        args = ['git', 'verify-tag', tag]
        try:
            with open(os.devnull, 'w') as null:
                exitcode = subprocess.call(args, cwd=self.container.path,
                                           stdout=null, stderr=null)
                return exitcode == 0
        except OSError:
            print_args = ' '.join(pipes.quote(a) for a in args)
            raise VersionError("command failed: {}".format(print_args))

    def _tags(self):
        """
        Return a generator which yields versions from git tags.
        Raise ``VersionError`` on failure.
        """
        args = ['git', 'tag', '--points-at', 'HEAD']
        try:
            with open(os.devnull, 'w') as null:
                out = subprocess.check_output(args, cwd=self.container.path, stderr=null)
            for line in out.split('\n'):
                if line:
                    yield Version(line, self._verify(line))
        except (subprocess.CalledProcessError, OSError):
            print_args = ' '.join(pipes.quote(a) for a in args)
            raise VersionError("command failed: {}".format(print_args))

    def _rev(self):
        """Return the version created using the uppercase short SHA hash of HEAD prepended with
        'r'."""
        args = ['git', 'rev-parse', '--short', 'HEAD']
        try:
            with open(os.devnull, 'w') as null:
                out = subprocess.check_output(args, cwd=self.container.path, stderr=null)
            return Version('r' + out.strip().upper(), False)
        except OSError:
            print_args = ' '.join(pipes.quote(a) for a in args)
            raise VersionError("command failed: {}".format(print_args))

    def detect(self):
        """Return a generator which yields the current git tags and revision for the container."""
        if self._valid():
            for tag in self._tags():
                yield tag
            yield self._rev()
