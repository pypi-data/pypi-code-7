import argparse
import sys
import os

import pymuxinator.config as config
from pymuxinator.project import Project
from pymuxinator import exceptions, utils


def main():
    CLI(args=sys.argv[1:])


def start():
    args = sys.argv[1:]

    # if it's just `mux api` we want `mux start api`
    if len(args) >= 1:
        args = ['start'] + args

    CLI(args=args)


class CLI(object):
    valid_commands = (
        ('commands', 'list commands',),
        ('start', 'start project',),
        ('list', 'list all projects',),
    )

    def __init__(self, args):
        parser = argparse.ArgumentParser(description='Pymuxinator')
        sub_parsers = parser.add_subparsers(title='commands', description='valid commands')

        for command, help_text in self.valid_commands:
            if hasattr(self, command):
                sub_parser = sub_parsers.add_parser(command, help=help_text or '')

                # add arguments to sub_parser
                if hasattr(self, '_' + command):
                    getattr(self, '_' + command)(sub_parser)

                # set default function for sub_parser
                sub_parser.set_defaults(func=getattr(self, command))

        if len(sys.argv) <= 1:
            parser.print_help()
        else:
            args = parser.parse_args(args)
            args.func(args)

    def _start(self, parser):
        parser.add_argument('project', help='pymuxinator project to start')
        parser.add_argument('--preview', dest='preview', action='store_true', help='preview tmux commands')

    def start(self, args):
        project_name = args.project
        project = None

        try:
            project = Project.from_name(project_name)
        except exceptions.ProjectNotFoundError:
            print u"Project `%s` does not exist" % project_name
        except exceptions.ConfigParseError as e:
            print u"Project `%s` config could not be parsed (%s)" % (project_name, e.message)
        except exceptions.NoWindowsError:
            print u"Project `%s` contains no windows. Please include some windows." % project_name
        except exceptions.NoNameError:
            print u"Project `%s` didn't specify a `project_name`." % project_name
        else:
            commands = project.render()

            if args.preview:
                print commands
            else:
                utils.execute_cmd(commands)

    def commands(self, args):
        commands = list(self.valid_commands)
        commands = sorted(commands, key=lambda x: x[0])

        for command, help_text in commands:
            print command

    def list(self, args):
        configs = config.list_all()

        for config_file in configs:
            base = os.path.basename(config_file)
            print os.path.splitext(base)[0]

