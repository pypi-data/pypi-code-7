from os import mkdir, path

from bael.project.virtualenv import VirtualenvTask
from baelfire.application.commands.init.models import InitFile
from baelfire.dependencies import (
    AlwaysRebuild,
    FileDoesNotExists,
)
from baelfire.task import Task


class CreateDataDir(Task):
    name = 'Creating data directory'
    path = '/data'

    directorie_names = [
        'datadir',
    ]

    @property
    def directories(self):
        for name in self.directorie_names:
            yield self.paths[name]

    def generate_dependencies(self):
        for directory in self.directories:
            self.add_dependecy(FileDoesNotExists(directory))

    def make(self):
        for directory in self.directories:
            if not path.exists(directory):
                mkdir(directory)


class Develop(Task):

    def generate_links(self):
        self.add_link('bael.hatak.templates:FrontendIni')
        self.add_link('bael.project.virtualenv:Develop')
        self.add_link('bael.hatak.alembic:AlembicMigration')


class CommandTask(VirtualenvTask):

    def generate_dependencies(self):
        self.add_dependecy(AlwaysRebuild())

    def generate_links(self):
        self.add_link(Develop)


class Serve(CommandTask):
    name = 'Run development server'
    path = '/serve'

    def make(self):
        self.pserve('%(data:frontend.ini)s --reload' % (self.paths))

    def pserve(self, command, *args, **kwargs):
        command = self.paths['exe:pserve'] + ' ' + command
        return self.command([command], *args, **kwargs)


class Shell(VirtualenvTask):
    name = 'Run development shell'
    path = '/shell'

    def generate_dependencies(self):
        self.add_dependecy(AlwaysRebuild())

    def generate_links(self):
        self.add_link(Develop)

    def make(self):
        self.pshell('%(data:frontend.ini)s' % (self.paths))

    def pshell(self, command, *args, **kwargs):
        command = self.paths['exe:pshell'] + ' ' + command
        return self.command([command], *args, **kwargs)


class BaelfireInitFile(Task):

    path = '/initfile'

    def get_output_file(self):
        return InitFile.filename

    def make(self):
        initfile = InitFile()
        initfile.assign('bael.hatak.recipe:HatakRecipe')
        initfile.save()


class ProjectTemplates(Task):

    path = '/templates'

    def generate_links(self):
        self.add_link('bael.hatak.templates:InitPy')
        self.add_link('bael.hatak.templates:ManagePy')
        self.add_link('bael.hatak.templates:Routes')
        self.add_link('bael.hatak.templates:Settings')
        self.add_link('bael.hatak.templates:TestFixtures')
        self.add_link('bael.hatak.templates:TestCases')
        self.add_link('bael.hatak.templates:TestSettings')
        self.add_link('bael.hatak.templates:RedmeFile')


class Tests(CommandTask):
    name = 'Run tests'
    path = '/tests'

    def make(self):
        if 'g' in self.kwargs:
            self.tests('-g %s' % (self.kwargs['g'][0]))
        elif 'c' in self.kwargs:
            self.tests('-c %s' % (self.kwargs['c'][0]))
        else:
            self.tests()

    def tests(self, command='', *args, **kwargs):
        command = self.paths['exe:manage'] + ' tests ' + command
        return self.command([command], *args, **kwargs)


class TestsList(Tests):
    name = 'Show all tests'
    path = '/tests/list'

    def make(self):
        self.tests('-l')


class Coverage(CommandTask):
    name = 'Generate test coverage report'
    path = '/tests/coverage'

    def make(self):
        omits = ','.join(self.settings['coverage omits'])
        self.coverage('run --branch %(exe:manage)s tests' % self.paths, True)
        self.coverage('html --omit=%s' % (omits,), True)
        if 'browser' in self.kwargs:
            browser = self.kwargs['browser'][0]
            self.command(['%s htmlcov/index.html' % (browser)])

    def coverage(self, command='', *args, **kwargs):
        command = self.paths['exe:coverage'] + ' ' + command
        return self.command([command], *args, **kwargs)
