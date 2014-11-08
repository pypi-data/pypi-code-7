import pipes
import os
import subprocess

def shell_escape(string):
    return pipes.quote(string)

def expand_path(path):
    if path[0] == '~':
        return os.path.expanduser(path)
    else:
        return os.path.abspath(path)

def execute_cmd(cmd):
    return subprocess.check_output(cmd, shell=True)
