__author__ = 'Ruben Nielsen'

from backup2.helpers import HelperMixin

import re
import sys
import os


class Operation(HelperMixin):
    """
    Defines an operation that can be run by the BackupRunner.
    All methods defined which match the prefix will be run in
    alphabetical order.
    If you need the methods to run in a specific order, override
    the get_run_methods method to return a list of method names in the
    order you desire.
    """
    prefix = "run_"
    ignore_errors = False

    def get_run_methods(self):
        """
        returns the name of the functions that should be run in the order they should be run.
        """
        return sorted(filter(lambda x: x.startswith(self.prefix), dir(self)))

    def handle_error(self, error_message):
        return error_message

    def run(self):
        methods = self.get_run_methods()
        last_method = None
        for method in methods:
            m = getattr(self, method)
            try:
                m()
            except Exception as e:
                return str(m.__name__), self.handle_error(str(e))
            last_method = method
        return last_method, ''


class BackupRunner(object):
    operations = {}
    summary = {}
    success = True

    # Command line tool options
    ops_to_run = []
    ignore_errors = False
    verbose = False
    silent = False
    print_summary = False
    notification_email = ''

    # Email settings
    email_user = ""
    email_passwd = ""
    email_host = ""
    email_port = ""
    email_use_tls = True
    _email_configured = False

    def __init__(self, ops_to_run=[], ignore_errors=False, verbose=False, silent=False,
                 success=True, print_summary=False, notification_email=''):
        self.ops_to_run = ops_to_run
        self.ignore_errors = ignore_errors
        self.verbose = verbose
        self.silent = silent
        self.success = success
        self.print_summary = print_summary
        self.notification_email = notification_email

    def register(self, obj):
        """
        Registers a dictionary of operations with the BackupRunner
        :param obj: a dictionary of operations
        """
        if not isinstance(obj, dict):
            raise ValueError('Only dictionaries can be registered')
        for key, value in obj.items():
            if not isinstance(key, str):
                raise ValueError('Dictionary key must be of type str, not %s: %s' % (type(key), key))
            if not isinstance(value, Operation):
                raise ValueError('Dictionary values must be Operations, not %s: %s' % (type(value), value))
            self.operations = obj

    def configure_email(self, user, passwd, host, port, use_tls=True):
        """
        Sets up access to SMTP email server. This allows you to send emails from the backup runner

        :param user: SMTP username
        :param passwd: SMTP password
        :param host: SMTP host, e.g. smtp.example.com
        :param port: SMTP port, e.g. 1234
        :param use_tls: Set to True if you want Transport Layer Security
        """
        self.email_user = user
        self.email_passwd = passwd
        self.email_host = host
        self.email_port = port
        self.email_use_tls = use_tls
        self._email_configured = True

    def send_email(self, message, subject, recipient, author=None):
        if self._email_configured:
            sender = author or self.email_user
            pass
        else:
            raise ValueError('Email not configured. See configure_email')

    def _init_summary(self):
        summary = {}
        for label, op in self.operations.items():
            assert isinstance(op, Operation)
            summary[label] = [
                {'method_name': methodname, 'err': ''} for methodname in op.get_run_methods()
            ]

        self.summary = summary

    def _update_summary(self, op_label, method_name, error_message=''):
        assert op_label in self.summary.keys()

        for i in range(len(self.summary[op_label])):
            if self.summary[op_label][i]['method_name'] == method_name:
                self.summary[op_label][i]['err'] = error_message
                if error_message:
                    self.summary[op_label][i]['method_name'] = "(FAIL) %s" % self.summary[op_label][i]['method_name']
                else:
                    self.summary[op_label][i]['method_name'] = "(SUCCESS) %s" % self.summary[op_label][i]['method_name']

    def get_summary_print(self):
        summary = self.get_summary()
        output = ""
        indent = 2

        for label, op in summary.items():
            output += label + "\n"
            for data in op:
                output += " "*indent + data['method_name'] + "\n"
        return output


    def run(self, ops=[]):
        """
        Runs a list of registered operations (see register) and returns the outputs
        of the operations in a dictionary, where each output is listed under its name, e.g.

        {
            'op1': [True, 42, "Hello world"],
            'foo_op2': [...],
        }

        :param ops: A list of names of operations to be run.
        :return: A dictionary with the return values of the operations.
        """
        self._init_summary()
        for op_label, op in self.operations.items():
            if op_label in ops or ops == []:
                if self.verbose:
                    self._print('Running %s')
                method, err = op.run()
                self._update_summary(op_label, method, err)
                if err and not self.ignore_errors:
                    self.success = False
                    self._print(err)
                    break

    def get_usage(self):
        return """\
        python <script_name> [Options] <Operations>

        Options:
        --help, -h           : Print this message
        --verbose, -v        : More output
        --ignore_errors, -i  : By default, the script will stop if an operation fails.
                               Set this option to ignore failures, and run the whole
                               suite.
        --summary, -s        : Print a summary of operations succeeded/failed
        --mailto <email>,
        -m <email>           : Send a notification to the given email if an error arises
        --silent, -l         : suppress all output to stdout. Overrules --verbose, -v

        Operations:
        A list of names that have been registered with the backup runner. Observe
        the following setup:

            runner = BackupRunner()
            runner.register({
                'foo': [...],
                'bar': [...],
                'baz': [...],
            })

        Now you can run your script with:

            python <script_name> [Options] foo baz

        This will run the operations 'foo' and 'baz', but not 'bar'
        """

    def get_summary(self):
        return self.summary

    def _get_command_line_arguments(self):
        script_name_index = 0
        for i in range(len(sys.argv)):
            if os.path.isfile(sys.argv[i]):
                script_name_index = i
            else:
                break
        return sys.argv[script_name_index + 1:]

    def _respond_to_config_error(self, message):
        """
        Handles errors in configuration and command line arguments
        :param message: A string describing the error
        """
        self._print('Unknown option: %s' % message)
        self.success = False
        return self.success

    def _respond_to_command_error(self, message):
        """
        Handles errors that occur when running an operation
        :param message: A string describing the error
        """
        if self.ignore_errors:
            return True
        else:
            self._print('Unknown option: %s' % message)
            self.success = False
            return self.success

    def _print(self, message):
        if not self.silent:
            print(message)

    def _is_email(self, string):
        return bool(re.compile(
            r'^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$'
        ).findall(string))

    def get_command_line_tool(self, *args):
        """
        Builds and runs the commandline tool. Can be provided with arguments directly
        as well as from stdin
        :param args: arguments to be treated like arguments from stdin
        """
        arguments = [x for x in args]
        arguments += self._get_command_line_arguments()

        for i in range(len(arguments)):
            arg = arguments[i]
            if arg.startswith('-'):
                if arg in ['--ignore_errors', '-i']:
                    self.ignore_errors = True
                elif arg in ['--verbose', '-v']:
                    self.verbose = True
                elif arg in ['--help', '-h']:
                    self._print(self.get_usage())
                    return True  # Ignore other operations and end script. Only print usage
                elif arg in ['--summary', '-s']:
                    self.print_summary = True
                elif arg in ['--silent', '-l']:
                    self.silent = True
                elif arg in ['--mailto', '-m']:
                    try:
                        email = arguments[i + 1]
                        if not self._is_email(email):
                            self._respond_to_config_error(
                                "%(arg)s is not a valid email" % {
                                    'arg': email,
                                }
                            )
                            break
                    except IndexError:
                        self._respond_to_config_error(
                            "%(arg)s must be given an email as argument, e.g. %(arg)s john@example.com" % {
                                'arg': arg,
                            }
                        )
                        break
                    self.notification_email = email
                    i += 1
                else:
                    self._respond_to_config_error("Unknown option: %s" % arg)
                    break
            else:
                if arg in self.operations.keys():
                    self.ops_to_run.append(arg)
                elif arg in ['true', 'test']:
                    pass  # Argument from unittests. Ignore it.
                else:
                    self._respond_to_config_error('%s is not a valid operation. Did you register it properly?' % arg)
                    break

        if not self.success:
            # Failed due to configuration
            self._print('No operations run. Resolve errors mentioned above!')
            return self.success

        self.run(self.ops_to_run)

        if not self.success and self.verbose:
            # Failed due to operation errors
            self._print('Some operations failed!')

        if self.print_summary:
            self._print(self.get_summary_print())
        return self.success
