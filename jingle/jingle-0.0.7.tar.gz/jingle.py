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
import simplejson as json

from StringIO import StringIO
from ConfigParser import SafeConfigParser, Error as ConfigError
from jinja2 import Template
from jinja2.exceptions import TemplateSyntaxError as JinjaError

# ------------------------------------------------------------------------------

__version__ = "0.0.7"
__author__  = "Kris Kovalik"

# ------------------------------------------------------------------------------

class CircularInheritanceError(ConfigError):
    pass

# ------------------------------------------------------------------------------

class AwesomeConfigParser(SafeConfigParser):

    def __init__(self, *args, **kwargs):
        SafeConfigParser.__init__(self, *args, **kwargs)
        self.fp = StringIO()
        self.superfiles = []

    def parse(self, fname):
        path = os.path.abspath(fname)
        self.fp.write("[root]\n")
        self.superfiles.append(path)
        self._parse(path)
        self.fp.seek(0)
        self.readfp(self.fp)

    def dict(self):
        dump = {}
        for key, value in self.items('root'):
            dump[key] = value
        return dump

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

class CLI(object):

    def __init__(self, argv):
        self.argv = argv
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
        try:
            config = AwesomeConfigParser()
            config.parse(self.argv[0])
            ctx = config.dict()
            self._debug_context(ctx)
            template = Template(sys.stdin.read())
            sys.stdout.write(template.render(ctx))
        except (IOError, ConfigError) as err:
            sys.stderr.write("Reading configuration failed!\n")
            sys.stderr.write("%s\n" % err)
            exit(1)
        except JinjaError as err:
            sys.stderr.write("Rendering failed!\n")
            sys.stderr.write("Template error: %s\n" % err)
            exit(1)

    def help(self, rc=0):
        print __doc__
        exit(rc)

    def version(self):
        print "Jingle v%s" % __version__
        exit(0)

    def _debug_context(self, ctx):
        if self.debug:
            sys.stderr.write("---\n")
            for key, value in ctx.items():
                sys.stderr.write("%s: %s\n" % (key, value))
            sys.stderr.write("---\n")

    def _anyarg(self, *args):
        return any(x in self.argv for x in args)
