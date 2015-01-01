"""Parallel and recursive git pull."""

import time
import subprocess as sp
import os
from threading import Thread
from progressbar import ProgressBar, Bar, Counter, Percentage, AdaptiveETA
from prettytable import PrettyTable
from termcolor import colored

class GitPuller(Thread):
    """A threaded execution of 'git status' and 'git pull'."""
    def __init__(self, git_dir_name):
        Thread.__init__(self)
        self._git_dir_name = git_dir_name
        self.local_ok = None
        self.git_pull_ok = None
        self.has_uncommitted_changes = None
        self.is_up_to_date = None
        self.git_local_output = None
        self.git_pull_output = None

    def run(self):
        git_status_process = sp.Popen('git status', cwd=self._git_dir_name,
                                      shell=True, stdout=sp.PIPE,
                                      stderr=sp.STDOUT)

        git_pull_process = sp.Popen('git pull', cwd=self._git_dir_name,
                                    shell=True, stdout=sp.PIPE,
                                    stderr=sp.STDOUT)

        self.git_local_output = git_status_process.communicate()[0]
        self.local_ok = git_status_process.returncode == 0
        self.has_uncommitted_changes = \
            "nothing to commit" not in self.git_local_output

        self.git_pull_output = git_pull_process.communicate()[0]
        self.git_pull_ok = git_pull_process.returncode == 0
        self.is_up_to_date = "Already up-to-date." in self.git_pull_output

def get_list_of_git_directories():
    """Returns a list of paths of git repos under the current directory."""
    dirs = [path[0] for path in list(os.walk('.')) if path[0].endswith('.git')]
    dirs = ['/'.join(path.split('/')[:-1]) for path in dirs]
    return sorted(dirs)

def run_git_concurrently(base_dir):
    """Runs the 'git status' and 'git pull' commands in threads and reports
    the results in a pretty table."""
    os.chdir(base_dir)
    git_dirs = get_list_of_git_directories()
    print("Processing %d git repos: %s" % (len(git_dirs), ', '.join(git_dirs)))

    widgets = [Percentage(),
               ' ', Bar(),
               ' ', Counter(),
               ' ', AdaptiveETA()]

    pbar = ProgressBar(widgets=widgets, maxval=len(git_dirs))
    pbar.start()

    threads = {git_dir:GitPuller(git_dir) for git_dir in git_dirs}
    for thread in threads.values():
        thread.start()

    while True:
        pbar.update(len([t for t in threads.values() if not t.is_alive()]))
        if all([not t.is_alive() for t in threads.values()]):
            break
        time.sleep(0.2)

    table = PrettyTable(["repo", "local", "pull"])
    table.align["repo"] = "l"
    table.align["local"] = "l"
    table.align["pull"] = "l"

    for git_dir in sorted(threads):
        thread = threads[git_dir]
        if thread.local_ok:
            if thread.has_uncommitted_changes:
                local_changes_text = colored(
                    'Uncommitted changes', 'green', attrs=['bold'])
            else:
                local_changes_text = colored('OK', 'green')
        else:
            local_changes_text = colored('Problem', 'red')

        if thread.git_pull_ok:
            if thread.is_up_to_date:
                pull_text = colored('OK', 'green')
            else:
                pull_text = colored('Changed', 'green', attrs=['bold'])
        else:
            pull_text = colored('Problem', 'red')

        table.add_row([git_dir, local_changes_text, pull_text])

    print(table)
    for git_dir in sorted(threads):
        if not threads[git_dir].git_pull_ok:
            thread = threads[git_dir]
            print colored('%s: ' % git_dir, 'red')
            print thread.git_pull_output
