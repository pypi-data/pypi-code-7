"""
Common exporter stuff.
"""

import os
import sys
import shutil
import codecs

from collections import defaultdict

import pkg_resources as pkg
from jinja2 import Environment, ChoiceLoader, PackageLoader, FileSystemLoader

from .plugin import Plugin, get_plugin, get_plugins
from .config import config, config_path, ConfigSection
from .util import make_directory, timespan
from .logger import log

from . import pkginfo
from . import flags

#: Mapping of exporter names to their classes.
exporters = None

#: Mapping of suffixes to archive formats.
archive_suffix = {".tar": "tar",
                  ".tar.gz": "gztar",
                  ".tgz": "gztar",
                  ".tar.bz2": "bztar",
                  ".zip": "zip"}


def get_exporter(name):
    "Get an exporter class given its name."

    return get_plugin(Exporter, name)


def get_exporters():
    "Yield all available exporters and their descriptions."

    for cls in get_plugins(Exporter):
        yield cls.name, cls.description


class Exporter(Plugin):
    """
    Base class for database exporters.

    Args:
        database (DitzDB): Database object.
    """

    category = "exporter"

    #: Name of the exporter.  This is the argument given to the ``export``
    #: command.
    name = None

    #: One-line description.  This gets printed when you list the
    #: available export formats.
    description = "undocumented"

    #: Package name.  If exporter is being installed via setuptools' plugin
    #: system, this should be set so that static and template files can be
    #: found in the package.
    package = None

    #: Exporter file suffix.  This is usually the same as the exporter name
    #: string.
    suffix = None

    #: If the exporter uses static files, this is the subdirectory of
    #: ``static`` to find them.  Usually the same as the ``name``
    #: attribute.
    static_dir = None

    #: If the exporter uses templates, this is the subdirectory of
    #: ``templates`` to find them.  Usually the same as the ``name``
    #: attribute.
    template_dir = None

    def __init__(self, database):
        #: The issue database being exported.
        self.db = database

        #: Configuration variables.
        self.config = ConfigSection(self.name, 'export', config)

        #: Available configuration options.  A list of tuples of the format
        #: (name, default, description).
        self.options = []

        #: Mapping of template names to loaded templates.
        self.templates = {}

        #: Template environment.
        self.env = None

        # Build search paths to static and template files.
        self.paths = defaultdict(list)

        for name, dirname in (("static", self.static_dir),
                              ("templates", self.template_dir)):
            if dirname is not None:
                for dirpath in (self.db.issuedir, config_path()):
                    path = os.path.join(dirpath, name, dirname)
                    self.paths[name].append(path)

        # Set up template environment if required.
        if self.template_dir is not None:
            paths = self.paths['templates']
            templates = os.path.join('templates', self.template_dir)
            package = self.package or __name__

            loaders = [FileSystemLoader(paths),
                       PackageLoader(package, templates)]

            self.env = Environment(loader=ChoiceLoader(loaders),
                                   trim_blocks=True, lstrip_blocks=True)

        # Add common filters.
        def issues(item):
            attr = item.__class__.__name__.lower()
            return [issue for issue in self.db.issues
                    if getattr(issue, attr) == item.name]

        rmap = {rel.name: rel for rel in self.db.project.releases}
        cmap = {comp.name: comp for comp in self.db.project.components}

        def release(issue):
            return rmap.get(issue.release, None)

        def component(issue):
            return cmap[issue.component]

        def issuetype(issue):
            return flags.TYPE[issue.type]

        def inprogress(issue):
            time = issue.progresstime
            return timespan(time) if time > 0 else ""

        def dateformat(value, format="%Y-%m-%d"):
            return value.strftime(format)

        def timeformat(value, format="%Y-%m-%d %H:%M"):
            return value.strftime(format)

        self.add_filter(issues)
        self.add_filter(release)
        self.add_filter(component)
        self.add_filter(issuetype)
        self.add_filter(inprogress)
        self.add_filter(dateformat)
        self.add_filter(timeformat)

        self.setup()

    def export(self, dirname):
        """
        Export the issue database to the given directory.

        Args:
            dirname (str): Directory to write files into.
        """

        # If output directory looks like the name of an archive, deduce
        # format and adjust the name.
        archive = None
        for suffix in archive_suffix:
            if dirname.endswith(suffix):
                dirname = dirname.replace(suffix, "")
                archive = archive_suffix[suffix]

        # Create output directory.
        make_directory(dirname, archive)

        # Preload all the templates if required.
        if self.template_dir is not None:
            for name in self.env.list_templates():
                self.templates[name] = template = self.env.get_template(name)
                log.info("loaded template from %s" % template.filename)

        # Write the exported files.
        self.write(dirname)

        # Copy static files, if any.  First those in the reversed search
        # path, so that earlier paths will override later ones.  Then copy
        # any files from the module that don't yet exist.
        if self.static_dir is not None:
            for path in reversed(self.paths['static']):
                if os.path.exists(path):
                    for name in os.listdir(path):
                        filename = os.path.join(path, name)
                        shutil.copy(filename, dirname)
                        log.info("copied %s to %s" % (filename, dirname))

            static = os.path.join('static', self.static_dir)
            package = self.package or __name__

            if pkg.resource_exists(package, static):
                for name in pkg.resource_listdir(package, static):
                    src = os.path.join(static, name)
                    dst = os.path.join(dirname, name)
                    if not os.path.exists(dst):
                        filename = pkg.resource_filename(package, src)
                        shutil.copy(filename, dirname)
                        log.info("copied %s to %s" % (filename, dirname))

        # Create archive and remove directory if required.
        if archive:
            shutil.make_archive(dirname, archive, root_dir=".",
                                base_dir=dirname, logger=log, verbose=True)
            shutil.rmtree(dirname)

    def setup(self):
        """
        Do exporter-specific setup.

        By default, this does nothing.
        """

    def add_filter(self, func, name=None):
        """
        Add a custom Jinja filter.

        Args:
            func (callable): Filter function.
            name (str, optional): Name to use in templates (same as
                function name, if None).
        """

        if self.env:
            self.env.filters[name or func.__name__] = func

    def add_config(self, name, default, desc=None):
        """
        Add an export configuration variable.

        The values of these can be set in the ``[export]`` section of a
        user config file, prepending the name of the exporter and an
        underscore.  For example, for the ``html`` exporter, the variable
        ``foo`` can be referred to as ``html_foo``.

        The :func:`write` method can access the value of configuration
        variables by calling methods of the exporter's :attr:`config`
        object.

        Args:
            name (str): Name of the variable.
            default (string or number): Its default value.
            desc (str, optional): One-line description.
        """

        self.config.add(name, str(default))
        self.options.append((name, default, desc))

    def write(self, dirname):
        """
        Write exported files to the given directory.

        This method must be overridden.  If using templates, it should call
        the :func:`render` method.

        Args:
            dirname (str): Directory to write files into.
        """

        raise NotImplementedError

    def render(self, dirname, templatefile, targetfile=None, **kw):
        """
        Render a single file from a template.

        Args:
            dirname (str): Directory to write file into.
            templatefile (str): Jinja template to use.
            targetfile (str, optional): Filename to write (same as
                 *templatefile*, if None).
            kw (dict): Template parameters.
        """

        # Get template.
        template = self.templates[templatefile]

        # Render template.
        kw.update(version=pkginfo.__version__, url=pkginfo.__url__)
        text = template.render(**kw)

        # Write it to file.
        path = os.path.join(dirname, targetfile or templatefile)
        with codecs.open(path, "w", encoding='utf-8') as fp:
            fp.write(text)

        log.info("wrote '%s'", path)

    def export_filename(self, item):
        """
        Return a unique export filename for a Ditz item.

        The filename is based on the item's ID (if it's an issue) or its
        name.  Each filename has the exporter suffix appended to it.

        Args:
            item (DitzObject): Ditz item.

        Return:
            Filename string.
        """

        clsname = item.__class__.__name__.lower()
        name = getattr(item, "id", None) or getattr(item, "name")
        return "%s-%s.%s" % (clsname, name, self.suffix)
