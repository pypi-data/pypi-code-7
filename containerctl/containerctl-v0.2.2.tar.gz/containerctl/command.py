"""Container commands."""
import sys
import yaml
from . import Container
from .errors import Error, TestError
from .version import Version
from clank import ArgumentCommand, HelpCommand, Manager, UsageCommand
from copy import deepcopy


def get_container(options):
    version = getattr(options, 'version', None)
    if version:
        version = Version(options.version, True)
    verify = getattr(options, 'verify', None)
    return Container.from_path(path=options.path, verify=verify, version=version)


class InfoCommand(ArgumentCommand):
    """Print information about a container."""
    name = 'info'

    def add_arguments(self):
        self.argparser.add_argument('-r', '--raw', dest='raw', action='store_true',
                                    help="Use the raw container congfiguration.")
        self.argparser.add_argument('-k', '--key', dest='key', nargs=1,
                                    help="Output only the specified toplevel key.")
        self.argparser.add_argument('-v', '--version', dest='version', nargs=1,
                                    help="Retreive info for this version of the container.")
        self.argparser.add_argument('-V', '--verify', dest='verify', action='store_true',
                                    help="Only retrieve verified tags and versions from the "
                                    "container.")
        self.argparser.add_argument('path', metavar='PATH', nargs='?',
                                    help="Use this path instead of the current directory.")

    def run(self, args):
        self.parse_args(args)
        try:
            container = get_container(self.options)
            data = container.to_dict(self.options.raw)
            if self.options.key:
                data = data.get(self.options.key)
            elif data.get('testing'):
                data['testing'] = deepcopy(data['testing'])
            if isinstance(data, (list, tuple, dict)):
                yaml.safe_dump(data, stream=sys.stdout,
                               explicit_start=False,
                               default_flow_style=False)
            elif isinstance(data, bool):
                print('true' if data else 'false')
            elif data is not None:
                print(data)
        except Error as e:
            print(e)
            return 1


class BuildCommand(ArgumentCommand):
    """Build a container."""
    name = 'build'

    def add_arguments(self):
        self.argparser.add_argument('-p', '--push', dest='push', action='store_true',
                                    help="Push the image after building.")
        self.argparser.add_argument('-l', '--latest', dest='latest', action='store_true',
                                    help="Also tag the container as 'latest'.")
        self.argparser.add_argument('-v', '--version', dest='version', nargs=1,
                                    help="The version of the container to build.")
        self.argparser.add_argument('-P', '--no-prebuild', dest='prebuild', action='store_false',
                                    help="Do not run the container's prebuild.")
        self.argparser.add_argument('-C', '--no-cache', dest='nocache', action='store_true',
                                    help="Do not use the Docker cache.")
        self.argparser.add_argument('-V', '--verify', dest='verify', action='store_true',
                                    help="Only build the container if it is verified.")
        self.argparser.add_argument('path', metavar='PATH', nargs='?',
                                    help="The path to the container to build.")

    def run(self, args):
        self.parse_args(args)
        try:
            container = get_container(self.options)
            built = container.build(self.options.prebuild,
                                    self.options.nocache,
                                    self.options.latest)
            for tag in built:
                print("{} built".format(tag))
            if self.options.push:
                pushed = container.push(self.options.latest)
                for tag in pushed:
                    print("{} pushed".format(tag))
            return 0
        except Error as e:
            print(e)
            return 1


class PushCommand(ArgumentCommand):
    """Push a container. The container will be built if it necessary."""
    name = 'push'

    def add_arguments(self):
        self.argparser.add_argument('-l', '--latest', dest='latest', action='store_true',
                                    help="Also push the 'latest' container image.")
        self.argparser.add_argument('-v', '--version', dest='version', nargs=1,
                                    help="The version of the container to build.")
        self.argparser.add_argument('-V', '--verify', dest='verify', action='store_true',
                                    help="Only push the container if it is verified.")
        self.argparser.add_argument('path', metavar='PATH', nargs='?',
                                    help="The path to the container to push.")

    def run(self, args):
        self.parse_args(args)
        try:
            container = get_container(self.options)
            if not container.is_built():
                container.build(latest=self.options.latest)
            tags = container.push(self.options.latest)
            for tag in tags:
                print("{} pushed".format(tag))
            return 0
        except Error as e:
            print(e)
            return 1


class RemoveCommand(ArgumentCommand):
    """Remove a container."""
    name = 'rm'

    def add_arguments(self):
        self.argparser.add_argument('-l', '--latest', dest='latest', action='store_true',
                                    help="Also remove the 'latest' container image.")
        self.argparser.add_argument('-v', '--version', dest='version', nargs=1,
                                    help="The version of the container to remove.")
        self.argparser.add_argument('path', metavar='PATH', nargs='?',
                                    help="The path to the container to remove.")

    def run(self, args):
        self.parse_args(args)
        try:
            result = 0
            container = get_container(self.options)
            for tag, success in container.remove(self.options.latest):
                if success:
                    print ("{} removed".format(tag))
            return result
        except Error as e:
            print(e)
            return 1


class RunCommand(ArgumentCommand):
    """Run a container."""
    name = 'run'

    def add_arguments(self):
        self.argparser.add_argument('-d', '--detach', dest='detach', action='store_true',
                                    help="Run the container in the background.")
        self.argparser.add_argument('-v', '--version', dest='version', nargs=1,
                                    help="The version of the container to run.")
        self.argparser.add_argument('-V', '--verify', dest='verify', action='store_true',
                                    help="Only run the container if it is verified.")
        self.argparser.add_argument('path', metavar='PATH', nargs='?',
                                    help="The path to the container to run.")

    def run(self, args):
        self.parse_args(args)
        try:
            container = get_container(self.options)
            if not container.is_built():
                container.build()
                print("{} built".format(container.tag))
            container.run(self.options.detach)
            if self.options.detach:
                print("{} running".format(container.tag))
        except Error as e:
            print(e)
            return 1


class KillCommand(ArgumentCommand):
    """Kill a container."""
    name = 'kill'

    def add_arguments(self):
        self.argparser.add_argument('path', metavar='PATH', nargs='?',
                                    help="The path to the container to kill.")

    def run(self, args):
        self.parse_args(args)
        try:
            container = Container.from_path(path=self.options.path)
            container.kill()
            print("{} killed".format(container.tag))
        except Error as e:
            print(e)
            return 1


class TestCommand(ArgumentCommand):
    """Test a container."""
    name = 'test'

    def add_arguments(self):
        self.argparser.add_argument('-r', '--rebuild', dest='rebuild', action='store_true',
                                    help="Rebuild the test container before running.")
        self.argparser.add_argument('-v', '--version', dest='version', nargs=1,
                                    help="The version of the container to run.")
        self.argparser.add_argument('-V', '--verify', dest='verify', action='store_true',
                                    help="Only run the container if it is verified.")
        self.argparser.add_argument('path', metavar='PATH', nargs='?',
                                    help="The path to the container to run.")

    def run(self, args):
        self.parse_args(args)
        try:
            container = get_container(self.options)
            if not container.is_built():
                container.build()
                print("{} built".format(container.tag))
            try:
                container.test(self.options.rebuild)
                print("{} test succeeded".format(container.tag))
            except TestError as e:
                print("{} test failed: exit code {}".format(container.tag, e.exit_code))
                return e.exit_code
        except Error as e:
            print(e)
            return 1


def run():
    """Run the ops tool."""
    try:
        return Manager([
            BuildCommand,
            HelpCommand,
            InfoCommand,
            KillCommand,
            PushCommand,
            RemoveCommand,
            RunCommand,
            TestCommand,
            UsageCommand,
        ]).run()
    except KeyboardInterrupt:
        print("interrupted")
        return 1
