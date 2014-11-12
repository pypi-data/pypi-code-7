"""
Import variable into your Django settings.py file, and whenever you define a
variable that could change depending on where the project is deployed, use
something like:

    DEBUG = variable("DEBUG")
    DEBUG = variable("DEBUG", default=False)

Here is a more useful example:

    import os

    # This needs to be a cryptographically secure random string. The default is
    # fine.
    SECRET_KEY = variable("SECRET_KET", os.urandom(64).decode("latin1"))

When your settings file is interpreted, a call to variable will look in a
variables module (which must be in your python path somewhere) to find the value
of the setting. If it is not defined, you are prompted to enter a valid Python
expression to set it, which is then written to the variables.py file in the
location of __main__
"""
from __future__ import print_function
import os
import sys
import inspect
import tokenize
import token
import readline
import importlib
from functools import partial
from collections import defaultdict
# these are imported so I can use mock easily to patch them. Also note that I
# alias raw_input to input for Python2
try:
    from builtins import input, print
except ImportError:
    from __builtin__ import raw_input as input, print

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

# the name of the module in the python path that we should load variables from
VARIABLES_MODULE = "variables"

# a dictionary of configuration options
variables = {}
try:
    variables_module = importlib.import_module(VARIABLES_MODULE)
    # the path to the VARIABLES_MODULE
    VARIABLES_PATH = os.path.abspath(os.path.join(variables_module.__file__))
    variables = dict((k, v) for k, v in variables_module.__dict__.items() if not k.startswith("__"))
except ImportError as e:
    # the variables module doesn't exist in the PYTHONPATH, so we will create
    # it in the same location as __main__
    VARIABLES_PATH = os.path.abspath(os.path.join(os.path.dirname(getattr(sys.modules["__main__"], '__file__', '')), VARIABLES_MODULE + ".py"))
    # the default location isn't in sys.path, so error out
    if os.path.dirname(VARIABLES_PATH) not in sys.path:
        raise RuntimeError("You need to create a %s.py file somewhere in your PYTHONPATH!" % (VARIABLES_MODULE))

    print(success("A %s.py file will be created in %s after you set a variable" % (VARIABLES_MODULE, VARIABLES_PATH)))


def variable(name, default=A_UNIQUE_VALUE):
    global variables

    # if the name of the variable is not defined, we need to prompt the user for it
    if name not in variables:
        has_default = default is not A_UNIQUE_VALUE

        comment = get_preceeding_comments()
        if comment:
            print(info(comment))

        if has_default:
            # write the default to stdin when input is promoted for
            readline.set_startup_hook(lambda: readline.insert_text(repr(default)))

        while name not in variables:
            # make sure we are at a tty device
            if not os.isatty(sys.stdin.fileno()):
                raise KeyError("You need to set the variable '%s' in %s (or somewhere else in your python path)." % (name, VARIABLES_PATH))

            val = input(warning(name) + " = ")
            # clear the startup hook since we only want to show the default
            # value once
            readline.set_startup_hook()

            if has_default and val == "":
                variables[name] = default
            else:
                try:
                    val = eval(val)
                except Exception as e:
                    print(danger(str(e)))
                    continue

                # we need to ensure the repr of the value is valid Python
                try:
                    eval(repr(val))
                except Exception as e:
                    print(danger("The value must have a repr that is valid Python (like a number, list, dict, or string)!"))
                    continue

                # everything is good, so we can actually save the value
                variables[name] = val

        # append the variable to the variables.py file
        with open(VARIABLES_PATH, "a+") as f:
            # write a newline if we're not at the beginning of the file, and
            # the previous line didn't end with \n
            write_new_line = f.tell() != 0 and not f.read().endswith("\n")
            if write_new_line:
                f.write("\n")
            f.write("%s" % comment + "\n" if comment else "")
            f.write("%s = %s\n" % (name, repr(val)))

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
