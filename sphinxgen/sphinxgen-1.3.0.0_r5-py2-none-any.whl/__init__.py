#! /usr/bin/env python
# vim: set fileencoding=utf-8: set encoding=utf-8:

"""
A utility module for generating basic sphinx rest files for each module and package
specified, recursively.

.. note::

    Please forgive me for this crappy code and crappier documentation. I hacked this
    together while working on another project. It's worth refactoring, if you'd like
    to do so, please feel free and send me a pull request:
    https://bitbucket.org/bmearns/sphinxgen

"""

import os, os.path
import sys
from fnmatch import fnmatch 
import jinja2
import argparse
import types
import logging

import sphinxgen.version

builtin_templates = {
    'package': """
``{{ fullname }}`` package
==============================================================================

{% if children|length != 0 %}

.. toctree::
    :maxdepth: 1

    {% for module in children %}
    {{ module.doc_name }}
    {% endfor %}

{% endif %}

.. automodule:: {{ fullname }}
    :members:
    :undoc-members:
    :show-inheritance:

""",

    'module': """
``{{ fullname }}`` module
==============================================================================

.. automodule:: {{ fullname }}
    :members:
    :undoc-members:
    :show-inheritance:

""",

    'index': """
Python Package Documentation
==============================

.. toctree::
    :maxdepth: 2

    {% for package in packages %}
    {{ package.doc_name }}
    {%- endfor %}

""",

}

class TemplateLoader(jinja2.BaseLoader):
    """
    A jinja2 template loaded that loads templates needed by `SphinxGen`.
    """
    def __init__(self, args):
        self.args = args
        self.base_dir = os.path.abspath(args.template_dir)

    def get_source(self, environment, template):
        """
        Returns the source for the named template.
        """
        if template == 'package':
            template_path = self.args.package_template
        elif template == 'module':
            template_path = self.args.module_template
        elif template == 'index':
            template_path = self.args.index_template
        else:
            template_path = template

        if template_path is not None:
            if not os.path.isabs(template_path):
                template_path = os.path.normpath(os.path.join(self.base_dir, template_path))
                if not template_path.startswith(self.base_dir):
                    raise Exception('Relative paths must remain inside the template directory: %s' % (template))
            if not os.path.exists(template_path):
                raise jinja2.TemplateNotFound(template_path)

            mtime = os.path.getmtime(template_path)
            with file(template_path, "r") as f:
                source = f.read().decode('utf-8')
            return source, template, lambda: mtime == os.path.getmtime(template_path)

        else:
            source = builtin_templates[template]
            return source, template, lambda: source == builtin_templates[template]

class SphinxGen(object):
    """
    The class that actually does the work.

    Initializing an instance runs the operation as well.
    """
    def __init__(self, parsed_args, log=None):
        """

        :param parsed_args:     This should be the namespace object returned by the `argument_parser` after parsing the command line options.

        """

        if isinstance(log, logging.Logger):
            log = log.getChild('sphinxgen')
        elif log is None or parsed_args.debug:
            log = logging.getLogger('sphinxgen')
            log.setLevel(logging.INFO)

        if isinstance(log, logging.Logger):
            if parsed_args.debug:
                debug_handler = logging.StreamHandler()
                debug_handler.setFormatter(logging.Formatter('%(name)s:%(levelname)s:%(asctime)s:%(message)s'))
                debug_handler.setLevel(logging.DEBUG)
                log.addHandler(debug_handler)
                log.setLevel(logging.DEBUG)
            else:
                standard_handler = logging.StreamHandler()
                standard_handler.setFormatter(logging.Formatter('%(name)s: %(message)s'))
                standard_handler.setLevel(logging.INFO)
                log.addHandler(standard_handler)

        self.log = log

        self.template_dir = os.path.abspath(parsed_args.template_dir)

        #Load out templates.
        jinja_env = jinja2.Environment(
            loader = TemplateLoader(parsed_args),
            autoescape=False
        )
        self.jinja_env = jinja_env

        try:
            self.package_template = jinja_env.get_template('package')
            log.debug('Loaded package_template')

            self.index_template = jinja_env.get_template('index')
            log.debug('Loaded index_template')

            if parsed_args.generate_modules:
                self.module_template = jinja_env.get_template('module')
                log.debug('Loaded module_template')
            else:
                self.module_template = None

        except jinja2.TemplateNotFound, e:
            raise Exception('One or more template files not found: %s' % (', '.join(e.templates)))

        log.debug('All templates loaded.')

        #get some args.
        self.overwrite = parsed_args.overwrite
        self.dry_run = parsed_args.dry_run
        self.prefix = parsed_args.prefix
        
        ### Dump builtin template files.
        template_dir = parsed_args.dump_templates
        if template_dir is not None:
            log.debug('Dumping template files as requested: %s', template_dir)
            if not os.path.exists(template_dir) and not self.dry_run:
                os.makedirs(template_dir)
            for name in builtin_templates:
                opath = os.path.join(template_dir, name + '.rst')
                log.info('Dumping built-in template file: %s', opath)
                if not self.dry_run:
                    log.debug('Not a dry run, writing file.')
                    with open(opath, 'wb') as ofile:
                        ofile.write(builtin_templates[name])

        output = os.path.normpath(parsed_args.output)

        #Collect all the packages, recursively.
        packages = []
        for package_dir in parsed_args.package_dirs:
            package = self.build_package(os.path.basename(package_dir), package_dir, output)
            if package is None:
                log.warning("package directory does not contain __init__ file: %s\n", package_dir)
            else:
                packages.append(package)

        log.debug('All packages processed: %d', len(packages))

        #Generate the index.
        if parsed_args.generate_index and len(packages):
            if parsed_args.index is None:
                index_name = parsed_args.prefix + 'index.rst'
            else:
                index_name = parsed_args.index + '.rst'
            log.debug('Generating index: %s', index_name)
            self.generate_output(self.index_template, {'packages': packages}, output, index_name, no_override=True)

        log.debug('SphinxGen complete.')


    def generate_output(self, template, context, output_dir, filename, no_override=False):
        """
        Writes output to the specified file. Given a jinja2 template object and
        the context for the template, it renders the template and writes the results
        to the specified path.

        If a file with the specified ``filename`` in the `template_dir` exists,
        then it is loaded as the template, instead of the template given. Unless
        ``no_override`` is ``True``, in which case the given template is always used.

        If the path exists, it is not modified unless `overwrite` is set. If
        `dry_run` is set, no output is actually generated.
        """
        overwrite = self.overwrite
        dry_run = self.dry_run

        if not no_override:
            possible_template = os.path.join(self.template_dir, filename)
            if os.path.exists(possible_template):
                self.log.info('Found template file for %s', filename)
                template = self.jinja_env.get_template(os.path.abspath(possible_template))

        opath = os.path.join(output_dir, filename)

        if not os.path.exists(opath) or overwrite:
            odir = os.path.dirname(opath)
            if not os.path.exists(odir) and not dry_run:
                self.log.debug('Creating output directory %s', odir)
                os.makedirs(odir)
            self.log.info("Generating %s", opath)
            contents = template.render(context)
            if not dry_run:
                self.log.debug('Not a dry run, writing to file.')
                with open(opath, 'wb') as ofile:
                    ofile.write(contents)
        else:
            self.log.info("File already exists: %s", opath)

        

    def build_package(self, package_name, package_dir, output_dir):
        """
        Does all the work (recursively) for a particular package, which is a directory
        with an :file:`__init__.py` file in it. Returns ``None`` if the specified
        directory (``package_dir``) is not actually a package (has not :file:`__init__.py`
        file). Otherwise returns a dictionary representing the some basic information
        about the package, it's subpackages, and its submodules (python files in the
        package directory).

        Generates the file for the package as well, plus all it's submodules, and all
        its sub packages. This is done through `generate_output`, so if `dry_run`
        is set, nothing will actually be written out.
        """
        self.log.debug('Building package %s from %s', package_name, package_dir)

        package_template = self.package_template
        module_template = self.module_template
        overwrite = self.overwrite
        dry_run = self.dry_run
        prefix = self.prefix

        dir_contents = os.listdir(package_dir)
        if '__init__.py' not in dir_contents:
            self.log.debug('Not a package, no __init__.py file.')
            return None

        modules = []
        sub_packages = []
        for path in dir_contents:
            fullpath = os.path.join(package_dir, path)
            if fnmatch(path, '*.py'):
                if path != '__init__.py':
                    self.log.debug('Found module file: %s', path)
                    mod_name = os.path.splitext(os.path.basename(path))[0]
                    fullname = package_name + '.' + mod_name
                    doc_name = prefix + fullname
                    modules.append(dict(
                        name = mod_name,
                        package = package_name,
                        fullname = fullname,
                        doc_name = doc_name,
                        path = fullpath,
                    ))
            elif os.path.isdir(fullpath):
                sub_package = self.build_package(package_name + '.' + path, fullpath, output_dir)
                if sub_package is not None:
                    sub_packages.append(sub_package)

        doc_name = prefix + package_name
        package_path = package_name.split('.')
        package = dict(
            name = package_path[-1],
            doc_name = doc_name,
            package = '.'.join(package_path[:-1]) if len(package_path) > 1 else None,
            fullname = package_name,
            path = package_dir,
            modules = modules,
            sub_packages = sub_packages,
            children = sub_packages + modules,
        )

        ofile = doc_name + '.rst'
        self.generate_output(package_template, package, output_dir, ofile)

        if module_template:
            for mod in modules:
                ofile = mod['doc_name'] + '.rst'
                self.generate_output(module_template, mod, output_dir, ofile)

        return package


_options = []
"""
Stores a simplified representation of all the options available in the `argument_parser`,
for use with the `sphinxgen` SetupTools command.
"""

argument_parser = argparse.ArgumentParser(
    prog='sphinxgen',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='Generate sphinx stub files for all modules in a python package.',
    usage='''
    %(prog)s [options] PACKAGE_DIR [PACKAGE_DIR [...]]
    %(prog)s [options] --dump-templates TEMPLATE_DIR [PACKAGE_DIR [...]]
    %(prog)s --help
''',
    epilog='''
Each PACKAGE_DIR specifies the path to a directory which defines a python
package (i.e., contains an __init__.py file. Packages will be scanned for
modules (contained python files) and subpackages (contained directories
which themselves contains an __init__.py file). Subpackages will be
recursively processed.

For each package found, a file will be generated using the template
specified by the --package-template option, and for each module found, a
file will be generated using the template specified by the --module-template
option. Generated files will be named according to the python path of the
package or module (plus an optional prefix specified by the --prefix option),
and placed in the directory specified by the required --output option.

After all packages are processed, an index file is generated information
about all of the processed packages, using the template specified by the
--index-template option. Note that if no PACKAGE_DIR arguments are specified,
no index will be generated.
''',
)
"""
An `~python:argparse.ArgumentParser` instance that can be used to parse the command line options for the
command line program. It is populated when the module is constructed.
"""

def _define_option(*args, **kwargs):
    """
    Takes a simplified description of a command line option, adds it to `argument_parser`,
    and also to `_options`. This supports a sort of intersection of the capabilities of
    both `~python:argparse` and the SetupTools command options.
    """
    argument_parser.add_argument(*args, **kwargs)
    _options.append((args, kwargs))

_define_option(
    '-o', '--output',
    action='store',
    dest='output',
    default='.',
    help='The directory where output will be written. The default is the current directory.',
)
_define_option(
    '--prefix',
    metavar='PREFIX',
    action='store',
    type=str,
    dest='prefix',
    default='',
    help=(
        'A prefix to use for every generated file name. '
        'If --index is used, the prefix will not be used for the generated '
        'index file.'
    ),
)
_define_option(
    '--overwrite',
    action='store_true',
    dest='overwrite',
    help='Overwrite any existing files.',
)
_define_option(
    '-n', '--dry-run',
    action='store_true',
    dest='dry_run',
    default=False,
    help= (
        'Do a dry run, do not actually generate any files, just print what '
        'would happen if we did.'
    ),
)
_define_option(
    '--index',
    metavar='PATH',
    dest='index',
    action='store',
    help=(
        'The path to the index file to generate (without extension). The default '
        'is "index", with appropriate prefix as specified by the --prefix option. '
        'if you explicitly use this option, the prefix will not be added.'
    ),
)
_define_option(
    '--no-index',
    dest='generate_index',
    action='store_false',
    default=True,
    help='Do not generate an index file.',
)
_define_option(
    '--no-modules',
    dest='generate_modules',
    action='store_false',
    default=True,
    help='Do not generate separate files for modules, only packages.',
)
_define_option(
    '--template-dir',
    metavar='DIR',
    action='store',
    type=str,
    dest='template_dir',
    default=None,
    help=(
        'The path to the base directory template files. This effects the resolution '
        'of paths specified for --package-template, --module-template, and '
        '--index-template, as well as any templates referenced from those templates. '
        'Templates referenced by absolute file-system path will be accessed directly, '
        'while templates referenced by any relative path will be loaded relative to '
        'this directory. The default is the current directory.'
    ),
)
_define_option(
    '--package-template',
    metavar='PATH',
    action='store',
    type=str,
    dest='package_template',
    default=None,
    help=(
        'The path to the jinja2 template file to use for generating package '
        'files. If not given, a built-in template will be used. Note that relative '
        'paths are resolved relative to the --template-dir.'
    ),
)
_define_option(
    '--module-template',
    metavar='PATH',
    action='store',
    type=str,
    dest='module_template',
    default=None,
    help=(
        'The path to the jinja2 template file to use for generating module '
        'files. See --package-template for more details. The default is '
        '"module.rst".'
    ),
)
_define_option(
    '--index-template',
    metavar='PATH',
    action='store',
    type=str,
    dest='index_template',
    default=None,
    help=(
        'The path to the jinja2 template file to use for generating the '
        'index file. See --package-template for more details. The default is '
        '"index.rst".'
    ),
)
_define_option(
    '--dump-templates',
    action='store',
    metavar='TEMPLATE_DIR',
    dest='dump_templates',
    default=None,
    help = (
        'Dump the built-in template files to the specified directory. This is '
        'useful as a starting point for creating your own template files. The '
        'template files are named package.rst, module.rst, and index.rst.'
    ),
)
_define_option(
    '--debug',
    action='store_true',
    dest='debug',
    default=False,
    help= (
        'Print detailed logs for debugging.'
    ),
)
_define_option(
    '--version',
    action='version',
    version='%(prog)s ' + sphinxgen.version.setuptools_string(),
),
_define_option(
    'package_dirs',
    metavar='PACKAGE_DIR',
    nargs='*',
    default = [],
    help='The package directories to process.',
)

def main(args=None):
    """
    The command line program. If this module is invoked as the main module, this
    function is called.

    This simply parses the ``args`` with ``argument_parser``, and passes them on
    to the `SphinxGen` factory method.

    :param args:    A sequence of command line arguments (like `python:sys.argv`)
        or ``None`` (in which case `python:sys.argv` is used).
    """
    args = argument_parser.parse_args(args)

    SphinxGen(args)
            
try:
    from setuptools import Command
except ImportError:
    Command = sphinxgen = None
else:

    from distutils import log, errors

    def _get_command_options():
        """
        A helper function used by `sphinxgen` to get the list of SetupTools command
        options, from `_options`.
        """
        options = []

        for names, kwargs in _options:
            long_name = None
            short_name = None
            for name in names:
                if name.startswith('--') and long_name is None:
                    long_name = name[2:]
                    if short_name is not None:
                        break
                elif name.startswith('-') and short_name is None:
                    short_name = name[1:]
                    if long_name is not None:
                        break
                elif long_name is None:
                    long_name = name
                    if short_name is not None:
                        break

            action = kwargs.get('action', 'store')
            if action == 'store' or action is None:
                long_name += '='
            elif action == 'version':
                continue

            help = kwargs.get('help', '')
            long_name = long_name.replace('_', '-')
            options.append((long_name, short_name, help))
                    
        return options


    class sphinxgen(Command):
        """
        A setuptools `~setuptools:setuptools.Command` for running `SphinxGen`.
        """

        description = "Generate base sphinx ReST files for python packages and modules."
        
        user_options = _get_command_options()

        def initialize_options(self):

            self._attributes = []
            for names, kwargs in _options:
                attr_name = kwargs.get('dest', None)
                if attr_name is None:
                    long_name = None
                    for name in names:
                        if name.startswith('--'):
                            long_name = name[2:]
                            break
                        elif name[0] != '-':
                            long_name = name
                            break
                    attr_name = long_name.replace('-', '_')

                action = kwargs.get('action', 'store')
                value = None
                if action == 'store' or action is None:
                    value = kwargs.get('default', None)
                elif action == 'store_true':
                    value = kwargs.get('default', False)
                elif action == 'store_false':
                    value = kwargs.get('default', True)
                elif action == 'version':
                    continue
                else:
                    raise Exception('Unhandled action: %s' % action)

                setattr(self, attr_name, value)
                self._attributes.append(attr_name)

            if self.output is None:
                self.output = os.path.join('sphinx', 'source')
                        

        def finalize_options(self):
            if isinstance(self.package_dirs, types.StringTypes):
                self.package_dirs = self.package_dirs.split(',')

        def run(self):
            try:
                SphinxGen(self, log=log)
            except Exception, e:
                raise errors.DistutilsError(e)


if __name__ == '__main__':

    main()

