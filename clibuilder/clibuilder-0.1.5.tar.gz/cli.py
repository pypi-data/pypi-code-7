"""Simple CLI-builder

Build interactive Command Line Interfaces, leaving the argument
validation and parsing logic to the `argparse` Standard Library module.
"""
import sys
import argparse

class CLI(object):
    """The Command Line Interface runner        
    """

    def __init__(self, prompt="> "):
        self.prompt = prompt

        # Commands this CLI is responsible for
        self.cmds = {}
        self.aliases = {}

        # Extension CLIs
        self.clis = {}

        # Build default commands
        self.add_func(self.print_help, ['h', 'help'])
        self.add_func(self.quit,       ['q', 'quit'])
        self.builtin_cmds = frozenset(('h', 'help', 'q', 'quit'))

    def add_func(self, callback, names, *args):
        """Adds a command to the CLI - specify args as you would to
        argparse.ArgumentParser.add_argument()
        """

        if isinstance(names, list):
            for name in names:
                self.add_func(callback, name, *args)
                self.aliases[name] = names
        elif isinstance(names, str):
            if names in self.cmds or names in self.clis:
                raise ValueError('Attempting to overwrite cmd or extern CLI: %s' % names)
            parser = argparse.ArgumentParser(prog=names)
            for cmd, spec in args:
                parser.add_argument(cmd, **spec)
            self.cmds[names] = (callback, parser)
        else:
            raise TypeError("Command must be specified by str name or list of names")

    def add_cli(self, prefix, other_cli):
        """Adds the functionality of the other CLI to this one, where all
        commands to the other CLI are prefixed by the given prefix plus a hyphen.

        e.g. To execute command `greet anson 5` on other cli given prefix cli2, you
        can execute the following with this CLI:
            cli2 greet anson 5

        """
        if prefix not in self.clis and prefix not in self.cmds:
            self.clis[prefix] = other_cli
        else:
            raise ValueError('Attempting to overwrite cmd or extern CLI: %s' % prefix)
    
    def _dispatch(self, cmd, args):
        """Attempt to run the given command with the given arguments
        """
        if cmd in self.clis:
            extern_cmd, args = args[0], args[1:]
            self.clis[cmd]._dispatch(extern_cmd, args)
        else:
            if cmd in self.cmds:
                callback, parser = self.cmds[cmd]
                try:
                    p_args = parser.parse_args(args)
                except SystemExit:
                    return
                callback(**dict(filter(lambda p:p[1] != None, p_args._get_kwargs())))
            else:
                self._invalid_cmd(command=cmd)

    def exec_cmd(self, cmdstr):
        """Parse line from CLI read loop and execute provided command
        """
        parts = cmdstr.split()
        if len(parts):
            cmd, args = parts[0], parts[1:]
            self._dispatch(cmd, args)
        else:
            pass

    def _invalid_cmd(self, command=''):
        print("Invalid Command: %s" % command)

    def print_help(self):
        """Prints usage of all registered commands, collapsing aliases
        into one record
        """
        seen_aliases = set()
        print('-'*80)
        for cmd in sorted(self.cmds):
            if cmd not in self.builtin_cmds:
                if cmd not in seen_aliases:
                    if cmd in self.aliases:
                        seen_aliases.update(self.aliases[cmd])
                        disp = '/'.join(self.aliases[cmd])
                    else:
                        disp = cmd
                    _, parser = self.cmds[cmd]
                    usage = parser.format_usage()
                    print('%s: %s' % (disp, ' '.join(usage.split()[2:])))
        print('External CLIs: %s' % ', '.join(sorted(self.clis)))

    def quit(self):
        """Quits the REPL
        """
        print('Quitting.')
        sys.exit(0)

    def run(self, instream=sys.stdin):
        """Runs the CLI, reading from sys.stdin by default
        """
        sys.stdout.write(self.prompt)
        sys.stdout.flush()
        while True:
            line = instream.readline()
            self.exec_cmd(line)
            sys.stdout.write(self.prompt)
            sys.stdout.flush()
