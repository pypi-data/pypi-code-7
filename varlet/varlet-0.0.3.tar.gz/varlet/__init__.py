"""
Import variable into your Django settings.py file, and whenever you define a
variable that could change depending on where the project is deployed, use
something like:

    DEBUG = variable("DEBUG")
    DEBUG = variable("DEBUG", default=False)

Here is a more useful example:

    from base64 import b64encode
    import os

    # This needs to be a cryptographically secure random string. The default is
    # fine.
    SECRET_KEY = variable("SECRET_KEY", default=b64encode(os.urandom(64)).decode("utf-8"))

When your settings file is interpreted, a call to variable will look in a
variables.yaml file (in the same directory as the settings file) to find the value
of the setting. If it is not defined, you are prompted to enter a valid Python
expression to set it, which is then written to the variables.yaml file.
"""
from __future__ import print_function
import os
import sys
import inspect
import yaml
import tokenize
import token
import readline
from functools import partial
from collections import defaultdict
# Python3 removed raw_input and change input() so it had the same semantics as
# raw_input
try:
    input = raw_input
except NameError:
    pass


class AnsiFormatCode:
    BLACK = 90
    RED = 91
    GREEN = 92
    YELLOW = 93
    BLUE = 94
    MAGENTA = 95 # purple
    CYAN = 96 # blue/green
    WHITE = 97


def ansi_format(format_code, string, *args, **kwargs):
    """
    Returns a string wrapped in the necessary boilerplate for rendering text with an ANSI format_code

    http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
    http://stackoverflow.com/questions/9468435/look-how-to-fix-column-calculation-in-python-readline-if-use-color-prompt
    """
    return "".join(['\001\033[', str(format_code), 'm\002', string.format(*args, **kwargs), "\001\033[0m\002"])

# create a few semantically named aliases for ansi_format. Matches twitter bootstrap naming.
success = partial(ansi_format, AnsiFormatCode.GREEN)
warning = partial(ansi_format, AnsiFormatCode.YELLOW)
info = partial(ansi_format, AnsiFormatCode.BLUE)
danger = partial(ansi_format, AnsiFormatCode.RED)

# to detect if a default value is specified, we check to see if it is not this
# object using the identity operator
A_UNIQUE_VALUE = float("nan")

# the first module to import this module determines the location of the config
# file. We can determine the location of the caller by inspecting the stack
VARIABLES_FILENAME = "variables.yaml"

# a dictionary of configuration options
variables = None
# the path to the configuration yaml file
variables_path = ""


def bootstrap():
    """
    Initialize the variables dictionary by loading the yaml file which is
    assumed to be located in the same directory as the 3rd thing on the stack
    frame
    """
    global variables, variables_path
    # The zero-th thing on the stack is this function, the one-th is the
    # variable() function, the two-th is the first module to call the variable
    # function, which is where the config yaml file is assumed to be
    frame = inspect.stack()[2]
    filename = frame[1]
    variables_path = os.path.join(os.path.dirname(filename), VARIABLES_FILENAME)
    # try to load the variables yaml file
    try:
        with open(variables_path, "r") as f:
            variables = yaml.safe_load(f) or {}
    except IOError:
        # the file doesn't exist yet, so we fake the variables
        variables = {}


def variable(name, default=A_UNIQUE_VALUE):
    global variables
    if variables is None:
        bootstrap()

    # if the name of the variable is not defined, we need to prompt the user for it
    if name not in variables:
        has_default = default is not A_UNIQUE_VALUE

        comment = get_preceeding_comments()
        if comment:
            print(info(comment))

        if has_default:
            readline.set_startup_hook(lambda: readline.insert_text(repr(default)))

        while name not in variables:
            # make sure we are at a tty device
            if not os.isatty(sys.stdin.fileno()):
                raise KeyError("You need to set the variable '%s' in '%s'. You can set this interactively if you run this script with stdin as a tty-like device" % (name, variables_path))

            val = input(warning(name) + " = ")
            # clear the startup hook since we only want to show the default
            # value once
            readline.set_startup_hook()

            if has_default and val == "":
                variables[name] = default
            else:
                try:
                    val = eval(val)
                    # make sure it is YAML serializable. This will throw an
                    # exception if it fails
                    yaml.safe_dump(val)
                    # everything is good, so we can actually save the value
                    variables[name] = val
                except yaml.representer.RepresenterError as e:
                    print(danger("The value must be YAML serializable (like a number, list, dict, or string)!"))
                except Exception as e:
                    print(danger(str(e)))

        # write the variable to the file (we do this *every* time we set
        # something, but that's OK since it only happens during the first
        # startup)
        with open(variables_path, "w") as f:
            yaml.safe_dump(variables, f, default_flow_style=False)

    return variables[name]


# we tokenize every file that imports variable and create a dict of dicts
# where the first key is the filename, and the second key is the line number of
# a comment in that file, and the value is the actual comment line
comments = defaultdict(dict)

def get_preceeding_comments():
    global comments
    # the variable call is back 2 places on the stack
    frame = inspect.stack()[2]
    # we want to find the comment line(s) that were written directly above the
    # call to variable. We figure out what file made the call, and tokenize
    # it
    filename = frame[1]
    line_no = frame[2]
    # the first time we come across this file, we need to tokenize it to find all the comments
    if filename not in comments:
        with open(filename) as f:
            for token_type, token_string, (srow, scol), (erow, ecol), line in tokenize.generate_tokens(f.readline):
                if token.tok_name[token_type] == "COMMENT":
                    comments[filename][srow] = token_string

    # create the doc for this variable by slurping up all the consecutive
    # comment lines that occur before the calling line in the calling file
    comment = []
    comments_in_this_file = comments[filename]
    # move up to the previous line
    line_no -= 1
    while comments_in_this_file.get(line_no, None) != None:
        comment.append(comments_in_this_file[line_no])
        line_no -= 1
    # we need to reverse the list of comment lines before joining, since the
    # lines were read from bottom to top
    comment = "\n".join(reversed(comment))

    return comment
