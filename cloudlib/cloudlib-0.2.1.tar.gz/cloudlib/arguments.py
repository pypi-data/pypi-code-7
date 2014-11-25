# =============================================================================
# Copyright [2014] [Kevin Carter]
# License Information :
# This software has no warranty, it is provided 'as is'. It is your
# responsibility to validate the behavior of the routines and its accuracy
# using the code provided. Consult the GNU General Public license for further
# details (see GNU General Public License).
# http://www.gnu.org/licenses/gpl.html
# =============================================================================
"""
>>> # THIS IS ONLY ADDED FOR TESTING
>>> import sys
>>> sys.argv = ['test_app', 'subparsed1', 'test']
>>> # THIS IS ONLY ADDED FOR TESTING

>>> from cloudlib import arguments
>>> arguments_dict = {
...     'shared_args': {
...         'shared_option1': {
...             'commands': ['--shared-option1'],
...             'help': 'Helpful Information'
...         }
...     },
...     'optional_args': {
...         'option1': {
...             'commands': ['--option1'],
...             'help': 'Helpful Information'
...         }
...     },
...     'positional_args': {
...         'possitional1': {
...             'help': 'Helpful Information',
...             'nargs': 1
...         }
...     },
...     'subparsed_args': {
...         'subparsed1': {
...             'help': 'Helpful Information',
...             'shared_args': ['shared_option1'],
...             'optional_args': {
...                 'mutually_exclusive': {
...                     'some_name': {
...                         'text': 'some description',
...                         'required': False
...                         'group': [
...                             'option1',
...                             'option2'
...                         ]
...                     }
...                 },
...                 'groups': {
...                     'some_name': {
...                         'text': 'some description',
...                         'group': [
...                             'other_option1',
...                             'other_option2'
...                         ]
...                     }
...                 },
...                 'option1': {
...                     'commands': ['--option1'],
...                     'default': False,
...                     'action': 'store_true',
...                     'help': 'Helpful Information'
...                 },
...                 'option2': {
...                     'commands': ['--option2'],
...                     'default': False,
...                     'action': 'store_true',
...                     'help': 'Helpful Information'
...                 },
...                 'other_option1': {
...                     'commands': ['--other-option3', '-O'],
...                     'metavar': '[STRING]',
...                     'type': str,
...                     'help': 'Helpful Information'
...                 },
...                 'other_option2': {
...                     'commands': ['--other-option4'],
...                     'metavar': '[STRING]',
...                     'type': str,
...                     'help': 'Helpful Information'
...                 }
...             }
...         }
...     }
... }
>>> args = arguments.ArgumentParserator(arguments_dict=arguments_dict)
>>> parsed_args = args.arg_parser()
>>> type(parsed_args)
<type 'dict'>
"""

import argparse
import os

from cloudlib import parse_ini


PARENT_ARGS = dict()


class ArgumentParserator(object):

    def __init__(self, arguments_dict, usage='%(prog)s', env_name='CLOUDLIB',
                 epilog=None, title=None, detail=None, description=None):
        """All variables are optional, and generally cosmetic.

            * If you wanted to change the program usage example, and or
              application name set the `usage` variable.

            * `env_name` pertains to any environment variables that are set and
              will be used as a prefix within the name of the available
              environment variable.

            * `eplilog` will allow you to set a string that is rendered at the
              end of the command when using ``--help``.

            * `detail` provides a short detailed information section under the
              example usage section.

            * `description` allows for more data to be used when describing the
              application.

        :param usage: `str`
        :param env_name: `str`
        :param epilog: `str`
        :param title: `str`
        :param detail: `str`
        :param description: `str`


        Example Usage:

        The arguments dictionary has several special keys which are reserved
        for building the CLI arguments.
        """
        self.usage = usage
        self.env_name = env_name
        self.epilog = epilog
        self.title = title
        self.detail = detail
        self.description = description
        self.arguments = arguments_dict

    @staticmethod
    def _add_arg(parser, value_dict):
        if value_dict is None:
            raise ValueError('value can not be None.')

        _opt_arg = value_dict.copy()
        parser.add_argument(
            *_opt_arg.pop('commands'),
            **_opt_arg
        )

    def _add_group(self, parser, groups, option_args):
        for k, v in groups.iteritems():
            group_text = v.pop('text', None)
            group_parser = parser.add_argument_group(group_text)
            _groups = v.pop('group', list())
            for item in _groups:
                self._add_arg(
                    parser=group_parser,
                    value_dict=option_args.pop(item)
                )

    def _add_mutually_exclusive_group(self, parser, groups, option_args):
        for k, v in groups.iteritems():
            group_text = v.pop('text', None)
            group_parser = parser.add_argument_group(group_text)
            ex_group_parser = group_parser.add_mutually_exclusive_group(
                required=v.pop('required', False)
            )
            for ex_arg in v.get('group', list()):
                ex_group = option_args.pop(ex_arg)
                if 'required' in ex_group:
                    ex_group.pop('required')

                self._add_arg(parser=ex_group_parser, value_dict=ex_group)

    def _add_opt_argument(self, opt_args, arg_parser):
        """Add an argument to an instantiated parser.

        :param opt_args: ``dict``
        :param arg_parser: ``object``
        """
        option_args = opt_args.copy()

        groups = option_args.pop('groups', None)
        if groups:
            self._add_group(
                parser=arg_parser,
                groups=groups,
                option_args=option_args
            )

        exclusive_args = option_args.pop('mutually_exclusive', None)
        if exclusive_args:
            self._add_mutually_exclusive_group(
                parser=arg_parser,
                groups=exclusive_args,
                option_args=option_args
            )

        for k, v in option_args.iteritems():
            self._add_arg(parser=arg_parser, value_dict=v)

    def _setup_parser(self):
        """Setup a configuration parser.

        Contains built in ``--system-config`` || ``-SC`` variable which is used
        to allow a user to set arguments in a configuration file which would
        then be processed from the "default" section of the provided file,
        assuming the file exists.

        :return: ``tuple``
        """
        # Set the prefix for environment variables
        ename = self.env_name.upper()
        env_name = '%s_CONFIG' % ename

        # Accept a config file
        conf_parser = argparse.ArgumentParser(add_help=False)
        conf_parser.add_argument(
            '--system-config',
            metavar='[FILE]',
            type=str,
            default=os.environ.get(env_name, None),
            help='Path to your Configuration file. This is an optional'
                 ' argument used to specify config. available as: env[%s]'
                 % env_name
        )
        known_args, remaining_argv = conf_parser.parse_known_args()
        conf_file = known_args.system_config
        if conf_file is not None:
            file_name = os.path.basename(conf_file)
            config = parse_ini.ConfigurationSetup(log_name=file_name)
            path_dir = os.path.dirname(conf_file)
            config.load_config(path=path_dir)
            config_args = config.config_args(section='default')
            known_args.__dict__.update(config_args)

        parser = argparse.ArgumentParser(
            parents=[conf_parser],
            usage=self.usage,
            description=self.description,
            epilog=self.epilog)

        # Setup for the positional Arguments
        if self.detail is not None:
            self.detail = '%s\n' % self.detail

        subparser = parser.add_subparsers(
            title=self.title,
            metavar=self.detail
        )
        return parser, subparser, remaining_argv

    def arg_parser(self, passed_args=None):
        """Setup argument Parsing.

        If preset args are to be specified use the ``passed_args`` tuple.

        :param passed_args: ``list``
        :return: ``dict``
        """
        parser, subpar, remaining_argv = self._setup_parser()
        if not isinstance(passed_args, list):
            passed_args = list()

        # Extend the passed args with the remaining parsed args
        passed_args.extend(remaining_argv)

        optional_args = self.arguments.get('optional_args')
        if optional_args:
            self._add_opt_argument(opt_args=optional_args, arg_parser=parser)

        subparsed_args = self.arguments.get('subparsed_args')
        if subparsed_args:
            for argument, value in subparsed_args.iteritems():
                if 'optional_args' in value:
                    optional_args = value.pop('optional_args')
                else:
                    optional_args = dict()

                if 'shared_args' in value:
                    set_shared_args = self.arguments.get('shared_args')
                    _shared_args = value.pop('shared_args', list())
                    for shared_arg in _shared_args:
                        optional_args[shared_arg] = set_shared_args[shared_arg]

                action = subpar.add_parser(
                    argument,
                    **value
                )
                action.set_defaults(parsed_command=argument)

                if optional_args:
                    self._add_opt_argument(
                        opt_args=optional_args, arg_parser=action
                    )

        positional_args = self.arguments.get('positional_args')
        if positional_args:
            for argument in positional_args.keys():
                _arg = positional_args[argument]

                parser.add_argument(
                    argument,
                    **_arg
                )

        # Return the parsed arguments as a dict
        return vars(parser.parse_args(args=passed_args))
