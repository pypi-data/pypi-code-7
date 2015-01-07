# encoding: utf-8

from __future__ import unicode_literals
from sys import argv

from docopt import docopt

from cli_runner.base import ServiceRegister, BaseService
from cli_runner.tools import unwrap_text


class ServiceLoader(object):
    help = """
        Usage:
            {name} [<service>] [...]
            {name} (-h | --help)

        Options:
            -h --help       This screen
            [<service>]     Run service
            [...]           Service options
    """

    def __init__(self):
        self.help = unwrap_text(self.help)
        super(ServiceLoader, self).__init__()

    def run(self):
        arguments = docopt(self.help,
                           argv=argv[1:2])
        service = arguments.get('<service>')
        if not service:
            self.show_services()
        else:
            self.run_service(service)

    def show_services(self):
        print self.help.strip().format(name=argv[0])
        print

        services = self.list_services()

        if not services:
            print 'No available services'
            return

        print 'Available services:'
        max_len = max(map(lambda line: len(line),
                          services.keys()))
        max_len += 4
        for name, Service in services.iteritems():
            print '    {name}{space}{short}'.format(
                name=name,
                space=' ' * (max_len - len(name)),
                short=self.get_service_short_description(Service)
            )

    def list_services(self):
        return ServiceRegister.services or {}

    def get_service(self, name):
        return ServiceRegister.services.get(name)

    def get_service_short_description(self, Service):
        if isinstance(Service, type) and issubclass(Service, BaseService):
            return Service.short_description()
        return ''

    def run_service(self, name):
        Service = self.get_service(name)
        if Service is None:
            print 'Unknown service "{}"!\n'.format(name)
            self.show_services()
            return

        service = Service()
        try:
            service.run()
        except KeyboardInterrupt:
            pass
        service.stop()
