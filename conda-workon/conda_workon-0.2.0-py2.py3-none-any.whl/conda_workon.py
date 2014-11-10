"""A workon command for conda

This implements a ``conda workon <envname>`` command which can be used
to spawn a new shell with the given conda environment activated.

The -l option can also be achieved using ``conda info --envs|-e``.
"""

from __future__ import absolute_import, print_function, division

import argparse
import os
import subprocess
import sys
import tempfile

import conda.config
import conda.misc


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--tmp', '-t',
        dest='spec',
        metavar='SPEC',
        nargs='?',
        const='python=3',
        help='Create a temporary environment, SPEC defaults to "python=3"',
    )
    group.add_argument(
        'envname',
        nargs='?',
        help='The environment to activate',
    )
    args = parser.parse_args(argv)
    if args.spec:
        workon_tmp(args.spec)
    else:
        workon(args.envname)


def workon_tmp(spec):
    """Create a temprorary conda envrionment in a subshell.

    Upon exiting the subshell the enviroment will be removed again.

    """
    with tempfile.TemporaryDirectory() as tmpdir:
        envdir = os.path.join(tmpdir, 'env')
        subprocess.check_call(['conda', 'create', '-p', envdir, spec])
        workon(envdir)


def workon(env):
    """Activate a conda environment in a subshell.

    :param env: Either the name of an environment or the full prefix
       of an environment.

    """
    path = os.environ['PATH'].split(os.pathsep)
    if os.path.isdir(env):
        envbindir = os.path.join(env, 'bin')
    else:
        envbindir = None
    for name, prefix in iter_envs():
        bindir = os.path.join(prefix, 'bin')
        try:
            path.remove(bindir)
        except ValueError:
            pass
        if name == env:
            envbindir = bindir
    if not envbindir:
        sys.exit('Unknown environment: {}'.format(env))
    path.insert(0, envbindir)
    environ = os.environ.copy()
    environ['PATH'] = os.pathsep.join(path)
    environ['CONDA_DEFAULT_ENV'] = env
    print('Launching subshell in conda environment.'
          '  Type "exit" or "Ctr-D" to return.')
    sys.exit(subprocess.call(environ['SHELL'], env=environ))


def iter_envs():
    """Iterator of the available conda environments

    Yields (name, prefix) pairs.
    """
    for prefix in conda.misc.list_prefixes():
        if prefix == conda.config.root_dir:
            yield conda.config.root_env_name, prefix
        else:
            yield os.path.basename(prefix), prefix
