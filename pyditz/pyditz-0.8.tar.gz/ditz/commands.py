"""
Ditz command handler.
"""

from __future__ import print_function

import os
import re
import sys
import six

from cmd import Cmd

from .database import DitzDB
from .config import config as userconfig
from .colorize import colorize, makeprompt
from .objects import Project, Config, find_config
from .files import write_config
from .util import print_columns, default_name, default_email, DitzError

from .flags import (STATUS, IN_PROGRESS, PAUSED, CLOSED, DISPOSITION,
                    FIXED, WONTFIX, REORG, BUGFIX, FEATURE, TASK,
                    UNRELEASED)

from six.moves import input


class DitzCmd(Cmd):
    #: Command prompt.
    prompt = makeprompt("Ditz:")

    #: Pager prompt.
    moreprompt = makeprompt("-- More (Y/n/q) --")

    def __init__(self, path=".", **kwargs):
        Cmd.__init__(self)

        #: Whether running interactively.
        self.interactive = kwargs.pop("interactive", False)

        #: Whether to skip asking for comments.
        self.nocomments = kwargs.pop("nocomment", False)

        #: Comment string to use in non-interactive mode.
        self.comment = kwargs.pop("comment", None)

        #: Whether searching in parent directories for database.
        self.search = kwargs.get("search", None)

        #: No. of terminal lines.
        self.termlines = kwargs.pop("termlines", 0)

        #: Database (read when required).
        self._db = None

        #: Arguments for reading database.
        self._dbargs = (os.path.realpath(path), kwargs)

        #: Last issue name mentioned.
        self.last_issuename = None

        #: Last release name mentioned.
        self.last_releasename = None

        #: Last 'log' argument.
        self.last_log = userconfig.getint('default', 'log')

        #: Last 'shortlog' argument.
        self.last_shortlog = userconfig.getint('default', 'shortlog')

        #: list of available commands.
        self.commands = set()

        # Set up list of known commands.
        for name in self.get_names():
            if name.startswith("do_"):
                self.commands.add(name[3:])

        # If interactive, set things up right now.
        if self.interactive:
            self.initdb()

    @property
    def db(self):
        self.initdb()
        return self._db

    def initdb(self):
        """
        Read or create the Ditz database, if not already done.
        """

        if not self._db:
            path, kwargs = self._dbargs
            if self.interactive:
                dirname, _ = find_config(path, search=self.search)
                if dirname:
                    self.write("Reading Ditz database in", dirname)
                    self.write()
                else:
                    self.write("Setting up Ditz database in", path)
                    self.write()
                    if not self.setup():
                        sys.exit()

            self._db = DitzDB.read(path, **kwargs)

        return self._db

    def setup(self):
        """
        Set up a database interactively.
        """

        config = self.getconfig()
        if config:
            name = config.name
            email = config.email
            issuedir = config.issue_dir
        else:
            return False

        path = os.path.join(issuedir, Project.filename)
        if os.path.exists(path):
            if write_config(config):
                self.write()
                self.write("Configuration written")
        else:
            path, kwargs = self._dbargs
            project = self.getline("Project name", os.path.basename(path))
            if not project:
                return False

            kwargs.pop('search')
            db = DitzDB(project, name, email, issuedir, path, **kwargs)
            db.write()

            self.write()
            self.write("Ditz database created in", path)

        return True

    # Command methods.

    def do_add(self, arg):
        "add -- Add an issue"

        self.initdb()

        title = self.getline("Title: ")
        if not title:
            return

        desc = self.gettext("Description")
        if desc is None:
            return

        types = {'b': BUGFIX, 'f': FEATURE, 't': TASK}

        while True:
            reply = self.getline("Is this a (b)ugfix, (f)eature or (t)ask? ")
            if reply and reply[0] in types:
                issuetype = types[reply[0]]
                break

        choices = self.db.components
        if len(choices) >= 2:
            comp = self.getchoice("component", choices)
            if not comp:
                return
        else:
            comp = None

        release = None
        releases = self.db.project.releases
        choices = [r.name for r in releases if r.status == UNRELEASED]
        if choices and self.getyesno("Assign to a release now?"):
            if len(choices) > 1:
                release = self.getchoice("release", choices)
            else:
                release = choices[0]
                self.write("Assigning to release", release)

            if not release:
                return

        default = self.db.config.username
        prompt = 'Issue creator (enter for "%s"): ' % default
        reporter = self.getline(prompt)
        comment = self.getcomment()
        if comment is None:
            return

        issue = self.db.add_issue(title, desc, type=issuetype,
                                  reporter=reporter, release=release,
                                  component=comp, comment=comment)

        name = self.last_issuename = self.db.issue_name(issue)
        self.write("Added issue", name)
        return True

    def do_add_component(self, arg):
        "add-component [name] -- Add a component"

        self.initdb()

        name = self.getarg(arg, 1) or self.getline("Name: ")
        if not name:
            return

        self.db.add_component(name)
        self.write("Added component", name)
        return True

    def do_add_reference(self, arg):
        "add-reference <issue> -- Add a reference to an issue"

        self.initdb()

        issue, name = self.getissue(arg, 1)
        if not issue:
            return

        self.write("Adding a reference to %s: %s" % (name, issue.title))
        text = self.getline("Reference: ")
        if not text:
            return

        comment = self.getcomment()
        if comment is None:
            return

        self.db.add_reference(issue, text, comment=comment)
        self.write("Added reference to", name)
        return True

    def do_add_release(self, arg):
        "add-release [name] -- Add a release"

        self.initdb()

        name = self.getarg(arg, 1) or self.getline("Name: ")
        if not name:
            return

        self.write("Adding release", name)
        comment = self.getcomment()
        if comment is None:
            return

        self.db.add_release(name, comment=comment)
        self.write("Added release", name)
        return True

    def do_archive(self, arg):
        "archive <release> [dir] -- Archive a release"

        self.initdb()

        name = self.getrelease(arg, 1)
        if not name:
            return

        path = self.getarg(arg, 2)
        if not path:
            path = "ditz-archive-%s" % name

        self.db.archive_release(name, path)
        self.write("Archived to", path)

    def do_assign(self, arg):
        "assign <issue> [release] -- Assign an issue to a release"

        self.initdb()

        issue, name = self.getissue(arg, 1)
        if not issue:
            return

        if issue.release:
            self.write("Issue %s currently assigned to release %s"
                       % (name, issue.release))
        else:
            self.write("Issue %s not currently assigned to any release" % name)

        release = self.getarg(arg, 2)

        if not release:
            releases = self.db.project.releases
            choices = [r.name for r in releases if r.status == UNRELEASED]

            if issue.release and issue.release in choices:
                choices.remove(issue.release)

            if not choices:
                self.error("no other release available")
                return

            if len(choices) > 1:
                release = self.getchoice("release", choices)
            else:
                release = choices[0]

        if not release:
            return

        if release == issue.release:
            self.error("already assigned to release %s" % release)
            return

        if not self.db.get_release(release):
            self.error("no release with name %s" % release)
            return

        self.write("Assigning to release", release)
        comment = self.getcomment()
        if comment is None:
            return

        self.db.set_release(issue, release, comment=comment)
        self.write("Assigned", name, "to", release)

        return True

    def do_changelog(self, arg):
        "changelog <release> -- Generate a changelog for a release"

        self.initdb()

        name = self.getrelease(arg, 1)
        if not name:
            return

        self.write(self.db.show_changelog(name))
        return True

    def do_config(self, arg):
        "config [<section>] -- show configuration settings"

        section = self.getarg(arg, 1)

        if not section:
            userconfig.write(sys.stdout)
            return True

        if not userconfig.has_section(section):
            self.error("no config section called '%s'" % section)
            return False

        for name in sorted(userconfig.options(section)):
            self.write(name, '=', userconfig.get(section, name))

        return True

    def do_close(self, arg):
        "close <open_issue> -- Close an issue"

        self.initdb()

        issue, name = self.getissue(arg, 1)
        if not issue:
            return

        self.write("Closing issue %s: %s" % (name, issue.title))

        disp = DISPOSITION
        revdisp = {disp[x]: x for x in disp}
        choices = (disp[FIXED], disp[WONTFIX], disp[REORG])
        choice = self.getchoice("disposition", choices)
        if not choice:
            return

        disp = revdisp[choice]
        comment = self.getcomment()
        if comment is None:
            return

        self.db.set_status(issue, CLOSED, disposition=disp, comment=comment)
        self.write("Closed issue", name, "with disposition", choice)
        return True

    def do_comment(self, arg):
        "comment <issue> -- Comment on an issue"

        self.initdb()

        issue, name = self.getissue(arg, 1)
        if not issue:
            return

        self.write("Commenting on %s: %s" % (name, issue.title))

        comment = self.getcomment()

        if comment:
            self.db.add_comment(issue, comment)
            self.write("Comments recorded for", name)
        else:
            self.write("Empty comment, aborted")

        return True

    def do_drop(self, arg):
        "drop <issue> -- Drop an issue"

        self.initdb()

        issue, name = self.getissue(arg, 1)
        if not issue:
            return

        self.db.drop_issue(issue)
        self.write("Dropped %s.  Other issue names may have changed." % name)
        return True

    def do_edit(self, arg):
        "edit <issue> -- Edit an issue"

        self.initdb()
        return self.unimplemented()

    def do_export(self, arg):
        "export <format> [path] -- Export issue database"

        self.initdb()

        fmt = self.getarg(arg, 1)
        if not fmt:
            self.error("no export format specified")
            return

        path = self.getarg(arg, 2) or fmt
        self.db.export(fmt, path)
        self.write("Exported issues to '%s'" % path)

        return True

    def help_export(self):
        from .exporter import get_exporters

        self.write(self.do_export.__doc__)
        self.write()
        self.write("available formats:")

        for name, desc in get_exporters():
            self.write("    %s -- %s" % (name, desc))

        return True

    def do_grep(self, arg):
        "grep <string> -- Show issues matching a string or regular expression"

        self.initdb()

        string = self.getarg(arg)
        if not string:
            self.error("no regexp specified")
            return

        try:
            regexp = re.compile(string)
        except re.error as msg:
            self.error("invalid regexp: %s" % six.text_type(msg))
            return

        self.write(self.db.show_grep(regexp) or "No matching issues")
        return True

    def do_help(self, arg):
        "help [command] -- Display help, optionally on a command"

        Cmd.do_help(self, arg)
        return True

    def do_init(self, arg):
        "init -- Initialize the issue database for a new project"

        dirname, _ = find_config(self._dbargs[0], search=self.search)
        if dirname:
            self.error("Ditz database already exists in %s" % dirname)
            return

        self.setup()

    def do_log(self, arg):
        "log [count] -- Show recent activity"

        self.initdb()

        count = self.getint(arg, 1)
        if count is None:
            count = self.last_log
        else:
            self.last_log = count

        self.write(self.db.log_events(count=count, verbose=True))
        return True

    def do_reconfigure(self, arg):
        "reconfigure -- Rerun configuration script"

        db = self.db
        config = self.getconfig(db.config)
        if config:
            db.config = config
            db.config.write(db.path)
            self.write("Configuration written")

    def do_release(self, arg):
        "release <unreleased_release> -- Release a release"

        self.initdb()

        name = self.getrelease(arg, 1)
        if not name:
            return

        comment = self.getcomment()
        if comment is None:
            return

        self.db.release_release(name, comment)
        self.write("Released", name)
        return True

    def do_releases(self, arg):
        "releases -- Show releases"

        self.initdb()

        self.write(self.db.show_releases() or "No releases")
        return True

    def do_set_component(self, arg):
        "set-component <issue> [component] -- Set an issue's component"

        self.initdb()

        issue, name = self.getissue(arg, 1)
        comp = self.getarg(arg, 2)
        if not issue:
            return

        self.write("Changing the component of issue %s: %s"
                   % (name, issue.title))

        choices = self.db.components
        if len(choices) < 2:
            self.error("this project does not use multiple components")
            return

        if comp and comp not in choices:
            self.error("unknown component: %s" % comp)
            return

        if not comp:
            if issue.component in choices:
                choices.remove(issue.component)

            comp = self.getchoice("component", choices)
            if not comp:
                return

        comment = self.getcomment()
        if comment is None:
            return

        self.db.set_component(issue, comp, comment)
        newname = self.db.issue_name(issue)

        if self.last_issuename == name:
            self.last_issuename = newname

        self.write("Issue %s is now %s.  Other issue names may have changed."
                   % (name, newname))

        return True

    def do_shortlog(self, arg):
        "shortlog [count] -- Show recent activity (short form)"

        self.initdb()

        count = self.getint(arg, 1)
        if count is None:
            count = self.last_shortlog
        else:
            self.last_shortlog = count

        self.write(self.db.log_events(count=count))
        return True

    def do_show(self, arg):
        "show <issue> -- Describe a single issue"

        self.initdb()

        issue, _ = self.getissue(arg, 1)
        if not issue:
            return

        self.write(self.db.show_issue(issue))
        return True

    def do_start(self, arg):
        "start <unstarted_issue> -- Start work on an issue"

        self.initdb()

        issue, name = self.getissue(arg, 1)
        if not issue:
            return

        if issue.status == IN_PROGRESS:
            self.error("already marked as " + STATUS[issue.status])
            return

        self.write("Starting work on %s: %s" % (name, issue.title))
        comment = self.getcomment()
        if comment is None:
            return

        self.db.set_status(issue, IN_PROGRESS, comment=comment)
        self.write("Recorded start of work for", name)
        return True

    def do_status(self, arg):
        "status [release] -- Show project status"

        self.initdb()

        release = self.getrelease(arg, 1, optional=True)
        self.write(self.db.show_status(release))

    def do_stop(self, arg):
        "stop <started_issue> -- Stop work on an issue"

        self.initdb()

        issue, name = self.getissue(arg, 1)
        if not issue:
            return

        if issue.status == PAUSED:
            self.error("already marked as " + STATUS[issue.status])
            return

        self.write("Stopping work on %s: %s" % (name, issue.title))
        comment = self.getcomment()
        if comment is None:
            return

        self.db.set_status(issue, PAUSED, comment=comment)
        self.write("Recorded stopping of work for", name)
        return True

    def do_todo(self, arg):
        "todo [-a,all] [release] -- Generate todo list"

        self.initdb()

        flag = self.getarg(arg, 1)
        if flag in ("-a", "all"):
            release = self.getrelease(arg, 2, optional=True)
            closed = True
        else:
            release = self.getrelease(arg, 1, optional=True)
            closed = False

        self.write(self.db.show_todo(release, closed))
        return True

    def do_unassign(self, arg):
        "unassign <assigned_issue> -- Unassign an issue from any releases"

        self.initdb()

        issue, name = self.getissue(arg, 1)
        if not issue:
            return

        if not issue.release:
            self.error("not assigned to a release")
            return

        relname = issue.release
        self.write("Unassigning %s: %s" % (name, issue.title))
        comment = self.getcomment()
        if comment is None:
            return

        self.db.set_release(issue, None, comment=comment)
        self.write("Unassigned", name, "from", relname)

        return True

    def do_validate(self, arg):
        "validate -- Fix or report problems with issue database"

        self.initdb()

        changes = self.db.validate()
        if changes:
            for idx, msglist in sorted(changes.items()):
                for msg in msglist:
                    self.write("issue %s: %s" % (idx, msg))
        else:
            self.write("No problems found")

        return True

    def do_shell(self, arg):
        "shell -- run a system command"
        os.system(arg)
        return True

    def do_path(self, arg):
        "path -- show the root Ditz database path"

        self.initdb()
        self.write(self.db.path)
        return True

    def do_quit(self, arg):
        "quit -- quit the interactive command loop"
        sys.exit()

    do_EOF = do_quit

    # Completion methods.

    def match_issue(self, text, line, beg, end):
        return startswith(self.db.issue_names, text)

    complete_add_reference = match_issue
    complete_assign = match_issue
    complete_close = match_issue
    complete_comment = match_issue
    complete_drop = match_issue
    complete_edit = match_issue
    complete_set_component = match_issue
    complete_show = match_issue
    complete_start = match_issue
    complete_stop = match_issue
    complete_unassign = match_issue

    def match_release(self, text, line, beg, end):
        return startswith(self.db.releases, text)

    complete_archive = match_release
    complete_changelog = match_release
    complete_release = match_release
    complete_status = match_release
    complete_todo = match_release

    def match_command(self, text):
        return startswith(self.commands, text)

    # Command hook methods.

    def onecmd(self, cmdline):
        # Get command and arguments.
        bits = cmdline.strip().split(None, 1)
        cmd = args = ""

        if len(bits) == 1:
            cmd = bits[0]
        elif len(bits) > 1:
            cmd, args = bits

        if cmd:
            # Substitute aliases, if any.
            if userconfig.has_option('alias', cmd):
                cmd = userconfig.get('alias', cmd)

            # Replace hyphens in command, to support original Ditz-style
            # commands.
            cmd = cmd.replace('-', '_')

            # Do completion on it.
            if cmd not in self.commands:
                matches = self.match_command(cmd)
                if len(matches) == 1:
                    cmd = matches[0]
                elif len(matches) > 1:
                    self.write("Ambiguous command: %s (%s)"
                               % (cmd, ", ".join(matches)))
                    return False

        # Run the command.
        try:
            retval = Cmd.onecmd(self, cmd + " " + args)
        except DitzError as msg:
            self.error(msg)
            retval = False

        return None if self.interactive else retval

    def emptyline(self):
        return self.onecmd("todo")

    def default(self, arg):
        msg = "unknown command: " + arg
        if self.interactive:
            msg += " (type 'help' for a list)"

        self.error(msg)
        return False

    # Input/output methods.

    def getarg(self, arg, idx=None):
        """
        Get a string argument.
        """

        if idx is None:
            return arg

        args = arg.split()
        if len(args) >= idx:
            return args[idx - 1]

        return None

    def getint(self, arg, idx, default=None):
        """
        Get an integer.
        """

        value = self.getarg(arg, idx)
        if not value:
            return default

        try:
            return int(value)
        except ValueError:
            self.error("expected an integer, not", value)
            return default

    def getissue(self, arg, idx):
        """
        Get an issue by name or ID.  Return it and its assigned name.
        """

        name = self.getarg(arg, idx)
        if not name and self.last_issuename:
            name = self.last_issuename

        if not name:
            self.error("no issue specified")
            return None, None

        self.last_issuename = name
        issue = self.db.get_issue(name)

        if not issue:
            issues = [i for i in self.db.issues if i.id.startswith(name)]
            count = len(issues)
            if count == 1:
                issue = issues.pop()
            elif count > 1:
                self.error("%d issues match ID '%s'" % (count, name))
                return None, None

        if not issue:
            self.error("no issue with name or ID '%s'" % name)
            return None, None

        return issue, self.db.issue_name(issue)

    def getrelease(self, arg, idx, optional=False):
        """
        Get a release by name.
        """

        name = self.getarg(arg, idx)
        if not name and optional:
            return None

        if not name and self.last_releasename:
            name = self.last_releasename

        if not name:
            self.error("no release specified")
            return None

        self.last_releasename = name
        if name not in self.db.releases:
            self.error("no release with name '%s'" % name)
            return None

        return name

    def getline(self, prompt="> ", default="", interrupt=True):
        """
        Get a single line of input.
        """

        if default:
            prompt = "%s (default '%s'): " % (prompt, default)

        # This is a bit naughty, and copies some internals of the Cmd
        # module.  But if the function had been exposed in the first place,
        # I wouldn't have to, would I?
        if self.use_rawinput:
            try:
                return input(prompt) or default
            except EOFError:
                return None
            except KeyboardInterrupt:
                if interrupt:
                    print()
                    return None
                else:
                    raise
        else:
            self.stdout.write(prompt)
            self.stdout.flush()
            line = self.stdin.readline()
            if not len(line.strip()):
                return default
            else:
                return line.rstrip('\r\n')

    def gettext(self, title=None, prompt="> ", endchar='.'):
        """
        Get multiline text.
        """

        if title:
            self.write(title + " (ctrl-c to abort, %s to finish)" % endchar)

        try:
            lines = []
            while True:
                line = self.getline(prompt, interrupt=False)
                if line is None or line == endchar:
                    return "\n".join(lines)

                lines.append(line)
        except KeyboardInterrupt:
            self.write()
            self.write("Aborted")
            return None

    def getchoice(self, thing, choices):
        """
        Get a choice of several things.
        """

        items = []
        for num, entry in enumerate(choices, 1):
            item = "%3d) %s" % (num, entry)
            items.append(item)

        print_columns(items)
        prompt = "Choose a %s (1--%d): " % (thing, len(choices))

        while True:
            reply = self.getline(prompt)

            try:
                return choices[int(reply) - 1]
            except (ValueError, IndexError):
                pass

    def getcomment(self):
        """
        Get a comment string.
        """

        if self.nocomments:
            return ""
        elif not self.interactive and self.comment:
            return self.comment
        else:
            return self.gettext("Comments")

    def getyesno(self, question, default=False):
        """
        Get the answer to a yes/no question.
        """

        prompt = question + " [%s] " % ("yes" if default else "no")

        while True:
            reply = self.getline(prompt)
            if not reply:
                return default
            if reply[0] in "yY":
                return True
            elif reply[0] in "nN":
                return False

    def getconfig(self, oldconfig=None):
        """
        Prompt for and return database configuration info.
        """

        default = oldconfig.name if oldconfig else default_name()
        name = self.getline("Your name", default)
        if name is None:
            return

        default = oldconfig.email if oldconfig else default_email()
        email = self.getline("Your email", default_email())
        if email is None:
            return

        issuedirs = userconfig.get('config', 'issuedirs').split()
        issuedir = issuedirs[0] if issuedirs else ".ditz-issues"
        default = oldconfig.issue_dir if oldconfig else issuedir
        issuedir = self.getline("Issue directory", default)
        if issuedir is None:
            return

        return Config(name, email, issuedir)

    def write(self, *args):
        if args:
            args = [six.text_type(s) for s in args]
            items = " ".join(args).split("\n")
            for num, line in enumerate(items, 1):
                print(colorize(line.encode('utf-8')))
                if self.termlines and num % (self.termlines - 1) == 0:
                    reply = input(self.moreprompt)
                    if reply and reply[0] in "nqNQ":
                        break
        else:
            print()

    def error(self, *args):
        self.write("Error:", *args)

    # Miscellaneous other stuff.

    def unimplemented(self):
        cmd = self.lastcmd.split()[0]
        self.write("Sorry, '%s' is not implemented yet" % cmd)
        return False


def startswith(items, text):
    return [x for x in items if x.startswith(text)]
