#!/usr/bin/python3

"""Jumprun, your command line companion
Usage:
    jr add <name> <command> [-d WORKDIR] [-f]
    jr rm all
    jr rm <name>
    jr show
    jr show all
    jr show <name>
    jr rename <old> <new>
    jr <name>
    jr -h
    jr -v
Commands:
    add         Add a new shortcut
    rm          Delete a shortcut
    rename      Rename a shortcut
    show        List all shortcuts
Options:
    -h, --help                  Show this screen.
    --version                   Show version.
    --workdir <dir>, -d <dir>   Working directory for the command
    --force, -f                 If shortcut already exists, overwrite it.
"""

import sqlite3
import subprocess
import os
import sys
from termcolor import colored
from docopt import docopt


def print_colored(string, color, on_color=None, attrs=None):
    """
    Print text using given color
    """
    print(colored(string, color, on_color=on_color, attrs=attrs))


def print_err(string):
    """
    Print error message
    """
    print_colored(string, 'red', attrs=['bold'])


def print_msg(string):
    """
    Print info message
    """
    print_colored(string, 'cyan')


def ask_yes_no(question, default="yes"):
    """
    Ask a yes/no question and return their answer.
    """
    valid = {
        "yes":  True,
        "y":    True,
        "ye":   True,
        "no":   False,
        "n":    False
    }

    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("Invalid default answer: '%s'" % default)

    while True:
        print(colored(question, 'green') +
              colored(prompt, 'cyan', attrs=['bold'], end=''))
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            print_err("Please respond with 'y' or 'n'.")


class JumpRun(object):

    def __init__(self):
        """
        Prepare database & init the object
        """

        self.args = docopt(__doc__, version=1.11)

        # creates a data folder in home dir
        path = os.path.expanduser('~/.jumprun')
        path = os.path.abspath(path)

        os.makedirs(path, exist_ok=True)
        self.dir = path

        # establish a connection
        self.init_db()

    def run(self):
        """
        Perform the specified action
        """

        if self.args['add']:
            self.action_add()

        elif self.args['rm']:
            self.action_rm()

        elif self.args['show']:
            self.action_show()

        elif self.args['rename']:
            self.action_rename()

        else:
            self.action_run_command()

    def get_data_file(self, name):
        """
        Get path to a file in the data directory
        """
        return os.path.join(self.dir, name)

    def init_db(self):
        """
        Init database and prepare tables
        """

        # database file
        db_path = self.get_data_file("data.sqlite")

        # comect and create cursor
        self.db = sqlite3.connect(db_path)
        self.cursor = self.db.cursor()

        # prep tables
        self.db_exec('''
            CREATE TABLE IF NOT EXISTS shortcuts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                path TEXT NOT NULL,
                command TEXT NOT NULL
            )
            ''')

    def db_query(self, query, args=None):
        """
        Execute a query in the DB
        """
        if args is None:
            self.cursor.execute(query)
        else:
            self.cursor.execute(query, args)

    def db_exec(self, query, args=None):
        """
        Execute a query in the DB
        """
        if args is None:
            self.db_query(query)
        else:
            self.db_query(query, args)

        self.db.commit()

    def db_fetch_one(self):
        """
        Fetch a results of last query
        """
        return self.cursor.fetchone()

    def db_fetch_all(self):
        """
        Fetch a results of last query
        """
        return self.cursor.fetchall()

    def shortcut_exists(self, name):
        """
        Check if a shortcut of given name already exists in the DB
        """

        self.db_query('''
            SELECT * FROM shortcuts WHERE name=?
            ''', (name,))

        pth = self.db_fetch_one()

        if pth is None or len(pth) == 0:
            return False
        else:
            return True

    def shortcut_str(self, path, cmd):
        """
        Get a string with colors describing a shortcut
        """

        s = colored('| path = ', 'cyan') + colored(path, 'yellow') + '\n' \
            + colored('| cmd  = ', 'cyan') + \
            colored(cmd, 'green', attrs=['bold'])

        return s

    def action_add(self):
        """
        Add a new shortcut
        """

        # prepare values for new shortcut
        path = self.args['--workdir'] or os.getcwd()
        name = self.args['<name>']
        cmd = self.args['<command>']

        overwrite = self.args['--force']

        # check for conflicts in DB
        if not overwrite and self.shortcut_exists(name):
            print_err('The shortcut "%s" already exists.' % name)
            return

        # if cmd has arguments, extract the command only
        cmd_parts = [x.strip() for x in cmd.split(' ')]
        cmd_real = cmd_parts[0]
        cmd_tail = ' '.join(cmd_parts[1:])

        # if cmd_real starts with ./, remove that
        if cmd_real.startswith('./'):
            cmd_real = cmd_real[2:]

        # path to the file (if it's in the folder)
        localfile = os.path.abspath(os.path.join(path, cmd_real))

        # check if the file is present at the path given
        if os.path.isfile(localfile):

            # file extension
            ext = os.path.splitext(cmd_real)[1]

            # check for exacutable bit
            # jar is executable, but cannot be run directly
            if os.access(localfile, os.X_OK) and not ext == '.jar':
                # file is executable
                cmd = ''

                if not cmd_real.startswith('/'):
                    cmd = './'

                cmd = cmd + cmd_real + ' ' + cmd_tail

            else:
                # not executable
                # try to find interpreter for the file

                interpreter = {
                    '.py': 'python',
                    '.rb': 'ruby',
                    '.pl': 'perl',
                    '.sh': 'sh',
                    '.php': 'php',
                    '.jar': 'java -jar',
                }.get(ext, None)

                # check if interpreter was found
                if interpreter is None:

                    msg = ('Could not make a shortcut to "%s":'
                           + '\n - not executable & unknown extension.') % localfile

                    print_err(msg)
                    return

                cmd = str(interpreter) + ' ' + \
                    str(cmd_real) + ' ' + str(cmd_tail)
        else:
            # use cmd, as given.
            pass

        if overwrite:
            self.db_exec('''
                    DELETE FROM shortcuts WHERE name=?
                    ''', (name,))
        # save to DB
        self.db_exec('''
            INSERT INTO shortcuts (name, path, command)
            VALUES (?, ?, ?)
            ''', (str(name), str(path), str(cmd)))

        # show OK message
        msg = ('Shortcut "%s" has been created.\n'
               + self.shortcut_str(path, cmd)) % name

        print_msg(msg)

    def action_rm(self):
        """
        Delete a shortcut
        """

        name = self.args['<name>']

        if self.args['all']:
            # delete all

            if ask_yes_no('Really delete ALL shortcuts?', default='no'):
                self.db_exec(''' DELETE FROM shortcuts ''')
                print_msg("All shortcuts deleted.")
            else:
                print_err("Aborted.")
                return

        else:
            # delete one

            # find by name
            self.db_exec('''
                SELECT id FROM shortcuts WHERE name=?
                ''', (name,))

            q = self.db_fetch_one()
            id = q[0]

            # delete if exists
            if q is None:
                print_err('Shortcut "%s" does not exist!' % name)

            else:
                self.db_exec('''
                    DELETE FROM shortcuts WHERE id=?
                    ''', (id,))

                # show OK message
                print_msg('Shortcut "%s" deleted.' % name)

    def action_rename(self):
        """
        Rename a shortcut
        """

        # get old and new name from args
        old = self.args['<old>']
        new = self.args['<new>']

        # select the old shortcut
        self.db_query('''
            SELECT id FROM shortcuts WHERE name=?
            ''', (old,))
        r = self.db_fetch_one()

        # error if old doesn't exist
        if r == None:
            print_err('Shortcut "%s" does not exist!' % old)
            return

        # error if new exists
        if self.shortcut_exists(new):
            print_err('Shortcut "%s" already exists!' % new)
            return

        id = r[0]

        # rename in DB
        self.db_exec('''
            UPDATE shortcuts SET name=? WHERE id=?
            ''', (new, id))

        # show OK message
        print_msg('Shortcut "%s" renamed to "%s".' % (old, new))

    def action_show(self):
        """
        Show shortcut(s) value
        """

        # helper function to display one row with colors
        # r = [name, path, command]
        def show_a_row(r):
            msg = colored('Shortcut: ', 'cyan') \
                + colored(r[0], 'white', attrs=['bold']) + '\n' \
                + self.shortcut_str(r[1], r[2]) + '\n'

            print(msg)

        name = self.args['<name>']

        if name is None or name == 'all':
            # select all shortcuts
            self.db_query('''
                SELECT name,path,command FROM shortcuts ORDER BY name
                ''')

            entries = self.db_fetch_all()

            # show the shortcuts
            if (entries is None) or (len(entries) == 0):
                print_err('No shortcuts defined.')
            else:
                for row in entries:
                    show_a_row(row)

        else:
            # select shortcut by name

            self.db_query('''
                SELECT name,path,command FROM shortcuts WHERE name=?
                ''', (name,))

            rec = self.db_fetch_one()

            # show the shortcut
            if rec is None:
                print_err('Shortcut "%s" does not exist.' % name)
            else:
                show_a_row(rec)

    def action_run_command(self):
        """
        Run a shortcut, if exists
        """

        name = self.args['<name>']

        # get entry from DB
        self.db_query('''
            SELECT path,command FROM shortcuts WHERE name=?
            ''', (name,))

        row = self.db_fetch_one()

        if row == None:
            print_err('Shortcut "%s" does not exist.' % name)
            return

        path = row[0]
        cmd = row[1]

        # show message
        msg = colored('JumpRun shortcut', 'white', attrs=['bold']) + '\n' + \
            self.shortcut_str(path, cmd) + '\n'
        print(msg)

        # cd to the folder & run the command
        os.chdir(path)

        try:
            subprocess.call(cmd, shell=True)
        except KeyboardInterrupt:
            print('')  # newline
            return


def main():
    jr = JumpRun()
    jr.run()


# start from terminal directly
if __name__ == "__main__":
    main()
