# -*- coding: utf-8 -*-
""" Command that checks which queries are executed on Django's project startup. """

import csv
import logging
from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connections, reset_queries
from django.utils.importlib import import_module
from six.moves import reload_module

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Writer(object):

    """ Sink type object that stores quereies and output statistics. """

    def __init__(self, stdout, output):
        """ Create Write object.

        :param stdout: File-like object to which save stats
        :param output: file name to which save queries logs
        """
        self.stdout = csv.writer(stdout)
        self.output = open(output, 'w') if output else None
        self.header = ['Module', 'Connection', 'Queries num', 'Total time']
        self.module_name = ''

    def set_module(self, module_name):
        """ Set currently processed module name.

        :param str module_name: module name
        """
        self.module_name = module_name

    def write(self, connection, queries):
        """ Write queries.

        :param connection: connection name
        :param queries: list of queries
        """
        self.write_stats(connection, queries)
        self.write_queries(connection, queries)

    def write_stats(self, connection, queries):
        """ Write queries stats to stdout.

        :param connection: connection name
        :param num: total number of queries
        """
        if self.header:
            self.stdout.writerow(self.header)
            self.header = None
        total_time = sum(float(query['time']) for query in queries)
        total_num = len(queries)
        self.stdout.writerow([self.module_name, connection, total_num, total_time])

    def write_queries(self, connection, queries):
        """ Write queries in log file.

        :param connection: connection name
        :param queries: list of queries
        """
        if self.output is not None:
            line = '%s:%s' % (self.module_name, connection)
            self.output.write('\n%s\n%s\n\n' % (line, '=' * len(line)))
            for i, query in enumerate(queries):
                row = '%s. %s - %s\n' % (i + 1, query['time'], query['sql'])
                self.output.write(row)

    def close(self):
        """ Close log file. """
        if self.output is not None:
            self.output.close()


class Command(BaseCommand):

    """ Command that checks which queries are executed on Django's project startup. """

    option_list = BaseCommand.option_list + (
        make_option('-o', '--output', dest='output', default=None,
                    help="File's name in which store executed queries"),
    )

    def handle(self, *args, **options):
        """ Run checks on given applications. """
        self.run_checks(args, options['output'])

    def run_checks(self, args, output):
        """ Run checks.

        :param args: iterable with application names
        :param output: file name to which save queries
        """
        modules = self.prepare_modules(args)

        writer = Writer(self.stdout, output)
        try:
            for module_name in modules:
                self.check_module(module_name, writer)
        finally:
            writer.close()

    def prepare_modules(self, args):
        """ Prepare list of modules that needs to be imported when checkin queries.

        :param args: iterable with application names
        :returns: list of module names
        """
        apps = args if args else settings.INSTALLED_APPS
        modules = []
        for app in apps:
            modules.append(app)
            for submodule in ['models', 'admin']:
                modules.append('%s.%s' % (app, submodule))
        return modules

    def check_module(self, module_name, writer):
        """ Check module queries.

        :param str module_name: module name
        :param writer: Writer object that will store queries
        """
        if self.reload_module(module_name):
            writer.set_module(module_name)
            self.store_queries(writer)

    def reload_module(self, module_name):
        """ Reload module and reset queries log.

        :param str module_name: module name
        :returns: True on success
        """
        try:
            mod = import_module(module_name)
            reset_queries()
            reload_module(mod)
        except (ImportError, RuntimeError):
            pass
        except Exception as e:
            log.warning(repr(e))
        else:
            return True

    def store_queries(self, writer):
        """ Store queries in writer.

        :param writer: Writer object that will store queries
        """
        for key in connections:
            queries = connections[key].queries
            if queries:
                writer.write(key, queries)
