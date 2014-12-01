"""Usage: jingle [OPTIONS] CONFIG_FILE < TEMPLATE_FILE

Renders TEMPLATE_FILE from standard input with context from given CONFIG_FILE.
Compiled file is printed to standard output.

Available options:

  -h, --help     Print this help screen.
  -v, --version  Print version number and exit.
  --debug        Print debug information on standard error.

"""

# ------------------------------------------------------------------------------

import os
import sys
import fileinput

from StringIO import StringIO
from ConfigParser import SafeConfigParser, Error as ConfigError

# ------------------------------------------------------------------------------

__version__ = "0.2.0"
__author__  = "Kris Kovalik"

# ------------------------------------------------------------------------------

class CircularInheritanceError(ConfigError):
    pass

# ------------------------------------------------------------------------------

class Context(SafeConfigParser):
    """ Customized parser for config files. It makes them one-level deep
    only and adds inheritance support. """

    def __init__(self, fname, *args, **kwargs):
        SafeConfigParser.__init__(self, *args, **kwargs)
        self.fp = StringIO()
        self.fname = fname
        self.superfiles = []
        self.parse()

    def parse(self):
        path = os.path.abspath(self.fname)
        self.fp.write("[root]\n")
        self.superfiles.append(path)
        self._parse(path)
        self.fp.seek(0)
        self.readfp(self.fp)
        self._dump()

    def dict(self):
        return self._dict

    def _dump(self):
        self._dict = {}
        for key, value in self.items('root'):
            self._dict[key] = value

    def _parse(self, path):
        with open(path) as f:
            for line in f:
                self._parseline(path, line)

    def _parseline(self, path, line):
        if len(line) > 0 and line[0:8] == "#inherit":
            superfile = line.replace("#inherit ", "", 1).strip()
            superpath = os.path.join(os.path.dirname(path), superfile)
            if superpath in self.superfiles:
                raise CircularInheritanceError(
                    "Circular inheritance detected on file: '%s'" % superfile)
            else:
                self.superfiles.append(superpath)
                self._parse(superpath)
        else:
            self.fp.write(line)

# ------------------------------------------------------------------------------

class Template(object):
    """ Simple wrapper around jinja's template powered by parameter files
    parsing functionality. """

    def __init__(self, template):
        self._template = template

    def render(self, ctx):
        from jinja2 import Template
        return Template(self._template).render(ctx.dict())

# ------------------------------------------------------------------------------

class CLI(object):
    """ Command line interface for jingle command. """

    def __init__(self, argv, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr):
        self.argv = argv
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.debug = False

        if '--debug' in self.argv:
            self.debug = True
            self.argv.remove('--debug')

    def run(self):
        if len(self.argv) != 1:
            self.help(rc=1)

        if self._anyarg('--help', '-h'):
            self.help(rc=0)
        elif self._anyarg('--version', '-v'):
            self.version()
        else:
            self.main()

    def main(self):
        from jinja2.exceptions import TemplateSyntaxError as JinjaError

        try:
            ctx = Context(self.argv[0])
            self._debug_context(ctx)
            tpl = Template(self.stdin.read())
            self.stdout.write(tpl.render(ctx))
        except (IOError, ConfigError) as err:
            self.stderr.write("Reading configuration failed!\n")
            self.stderr.write("%s\n" % err)
            exit(1)
        except JinjaError as err:
            self.stderr.write("Rendering failed!\n")
            self.stderr.write("Template error: %s\n" % err)
            exit(1)

    def help(self, rc=0):
        self.stdout.write(__doc__)
        exit(rc)

    def version(self):
        self.stdout.write("Jingle v%s\n" % __version__)
        exit(0)

    def _debug_context(self, ctx):
        if self.debug:
            self.stderr.write("---\n")
            for key, value in ctx.dict().items():
                self.stderr.write("%s: %s\n" % (key, value))
            self.stderr.write("---\n")

    def _anyarg(self, *args):
        return any(x in self.argv for x in args)
