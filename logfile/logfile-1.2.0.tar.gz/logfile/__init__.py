#!/usr/bin/env python
# coding: utf-8

# Python 2.7 Standard Library
import datetime
import importlib
import inspect
import os.path
import sys
import types
import weakref

# Third-Party Libraries
import pkg_resources

#
# Metadata
# ------------------------------------------------------------------------------
#
__name__    = "logfile"
__version__ = "1.2.0"
__author__  = u"Sébastien Boisgérault <Sebastien.Boisgerault@mines-paristech.fr>"
__license__ = "MIT License"
__url__     = "https://github.com/boisgera/logfile"
__summary__ = "File-based logging library"
__readme__  = "README.md"
__classifiers__ = [
  "Intended Audience :: Developers",
  "Operating System :: OS Independent",
  "Programming Language :: Python :: 2.7",
  "License :: OSI Approved :: MIT License",
  "Topic :: Software Development :: Libraries :: Python Modules",
  "Topic :: System :: Logging",
]

if os.path.exists(__readme__) and os.path.exists("logfile.py"):
    __doc__ = open(__readme__).read()
else:
    __doc__ = pkg_resources.resource_string(__name__, __readme__)

__doc__ = __summary__ + "\n" + __doc__ # support for pydoc conventions.

# ------------------------------------------------------------------------------
# TODO: for C/optimized code, issue a sub-module ("raw_logfile" for example ?
#       that can be used in place of the logfile. Frame trickeries are disabled,
#       naming has to be done manually. (Doable ?)
#
# TODO: *shared* configuration between all loggers to make logging cooperative.
#
# Design: given that all existing loggers shall *implicitly* refer to the config
#         (that holds for example the verbosity level), we have no choice
#         but to have a global module-level variable here. However, a user
#         of the logger module that intends to play nice and not scramble other
#         logger users may need some get/set config functions.       

# Doc: the global _Config instance has the following properties: 
#      - 'level' is a verbosity level: the higher it is, the more gets printed.
#      - 'output' is the common loggers output file object,
#      - 'format' is the customizable message formatting method. It may use
#        (the source logger object and) the message logged.
#      - [TODO]: 'filters': I'd like to have the way to specify a set of
#        (positive or negative ?) filters that may filter according to the
#        hierarchy of loggers context (say 'mystuff.deeper.blah') optionnaly
#        inferred at loggers creation time by the __main__ variable ?
#        CARE: this inference won't work if the module is used as a script ...
#        (doctest stuff may be affected)

# TODO: generalize the context so that we may say for example that we are in
#       audio.wave.write (function write in the audio.wave module) ? Dynamic
#       contexts ? That would be nice and quite easy I guess if I use
#       context managers.
#
# TODO: document automatic substitution of local variables in messages.
#
# TODO: have a look at 
# <http://stackoverflow.com/questions/4492559/python-code-to-get-current-function-into-a-variable> to get the (qualified) name of a function/method
# that is currently executed. Use it as an info for the logger context and
# drop explicit context naming ? Migrate the standard logfiles to the
# module toplevel ?

# TODO: register modules: build a code to qualified name map.

# TODO: use the inspiration from warnings module to extract more info from
#       the point of call (module, that could be the default tag, line, etc.)
#       Probably use the module info as the default tagging information to
#       limit the need for manual tagging ? By a suitable exploration of the
#       code object, we can even get to the function name. Would it work
#       for methods (get the class name ?). Nope. Same issue for methods
#       that we have for profiling, would require (SOME) source file
#       analysis (and does not always work ...). What about generated methods
#       or methods added in a class after its definition ? (Would not work
#       with source analysis right ?). Do the opposite and inspect all methods
#       of all classes in a module to identify them by code (code object I
#       mean) ? But that won't work with decorators or generated functions ...
#       I am not sure how, i should deal with that issue (and I am not sure
#       that both issues are the same). With an explicit
#       "logfile.tag" context manager ?
#       Mmm even for inner function, we still have the name. And that may
#       be good enough ? Otherwise we could find something with the lineno
#       if it is in the range of a function def or decorator ? And here,
#       we would have little choice but parsing ? Use getsourcelines from
#       inspect to do the job ? Use syntaxic analysis on top of that ?
#       Well maybe in a first approach, only deal with classes ? Or dont
#       even bother ?
#
#       Rk: it's hard to implement a system in which manual tagging can
#           override the automatic tagging ... How do we know if the
#           tagging was set for the current function or the previous one
#           in the call stack ? Fully automatic would be better ... (?)

# TODO: study the warnings API. Disable the warnings by default ? (would be
#       kind of redundant ?). Yes, but only in logfile.warning calls, restore
#       the filter state after that. Implement pre-post hooks as context
#       managers ?
#       ABOUT WARNINGS: logfile should probably NOT integrate warnings,
#       because some features would be redundant (filters, print to
#       stdout, etc.). The ability to turn warnings into errors could
#       be easily programmed in each module that needs it, and controlled
#       by a global function (think of `seterr` in `numpy`). No need to
#       offer that in logfile ...

# TODO: implement the full local / global / builtin namespaces in templating.

# TODO: replace the general hook system with an hardcoded system ? Hook only
#       for critical an error for the moment ?

#
# Logger API
# ------------------------------------------------------------------------------
#

# Im am still searching for a good way to have better tags, either automatically
# or manually ; both approaches are challenging. I'd rather have something
# automatic to be honest, this is less API and paradoxically less complicated
# to implement, a manual approach would probably have to mess with the identif
# of frames and a (active) frame to tags dictionary.
# Today, we end up with a module.function tag that does not understand closures 
# or methods. We could scan a module source code once and for all and try to 
# build a lines to name correspondance. Doit with an "auto_tag" function ?
# Offer the same service for MANUAL tagging (possible ?) ?

#_tags = {} # weakref.WeakKeyDictionary() does not work with frames :(
#def tag(name, _frame_depth=0):
#    frame = inspect.currentframe(_frame_depth + 1)
#    _tags[frame] = name

def tag(tag_):
    frame = inspect.currentframe(1)
    frame.f_locals["_logfile_tag"] = tag_

class LogFile(int):
    def __new__(cls, name, number, _hook=None):
        return int.__new__(cls, number)

    def __init__(self, name, number, _hook=None):
        self.name = name
        self._hook = _hook

    def get_frame(self, _frame_depth=0):
        frame = inspect.currentframe(_frame_depth + 1)
        if frame is None:
            raise ValueError("can't get the caller frame")
        return frame

    def get_tag(self, frame):
        tag = frame.f_locals.get("_logfile_tag")
        if tag is None:
            tag_parts = []
            code = frame.f_code
            module = inspect.getmodule(code)
            if module is not None:
                module_name = module.__name__
                tag_parts.append(module_name)
            function_name = frame.f_code.co_name
            # Logfiles can be called at the module level, get rid of <module>
            if function_name != "<module>": 
                tag_parts.append(function_name)
            tag = ".".join(tag_parts)
        return tag

    def get_message(self, message, frame):
        locals_ = frame.f_locals
        message = str(message).format(**locals_)
        return message

    def write(self, message):
        self(message, _frame_depth=1)

    def __call__(self, message, *args, **kwargs):
        _frame_depth = kwargs.get("_frame_depth", 0) + 1
        frame = self.get_frame(_frame_depth)
        message = self.get_message(message, frame)
        tag = self.get_tag(frame)
        date = datetime.datetime.now() # make a get_date method ?
        item = dict(logfile=self, message=message, tag=tag, date=date)

        if config.level >= self:
            config.output.write(config.format(**item))
            try:
                config.output.flush()
            except AttributeError:
                pass
        hook = self._hook
        if hook is not None:
            hook(message, *args, **kwargs)
    def __str__(self):
        return self.name

    def __repr__(self): # unspecified behavior
        return "Logfile({0.name!r}, {1})".format(self, int(self))
    

#
# Standard LogFiles
# ------------------------------------------------------------------------------
#

def critical_hook(message, status=None):
    if status is not None: # unspecified behavior
        sys.exit(status)   # override the message. 
    else:
        if message.endswith("\n"):
            message = message[:-1]
        sys.exit(message)

def error_hook(message, type=Exception, *args):
    if message.endswith("\n"):
        message = message[:-1]
    raise type(message, *args)

critical = LogFile("critical", -2, _hook=critical_hook)
error    = LogFile("error"   , -1, _hook=error_hook)
warning  = LogFile("warning" ,  0)
info     = LogFile("info"    ,  1)
debug    = LogFile("debug"   ,  2)  

#
# Shared Configuration
# ------------------------------------------------------------------------------
#

class Config(object):
    """
    Logging Configuration
    """
    def __init__(self, level=None, output=None, format=None):
        """
        The attributes of a `Config` instance are:

          - `level`: verbosity level: the higher it is, the more gets logged,
        
          - `output`: the real output file object behind all logfiles,
        
          - `format`: a message formatting function whose arguments are
            
              - `logfile`: the logfile that requested the logging, 
         
              - `message`: the message logged,

              - `tag`: a string that identifies the emitter function,

              - `date`: a `datetime.datetime` instance.
        """
        self.level = level or 0
        self.output = output or sys.stderr
        self.format = format or self._format
    def _format(self, **kwargs):
        return kwargs["message"] #+ "\n"

config = Config()

#
# Formatters
# ------------------------------------------------------------------------------
#

# TODO: provide a choice of formatters ?

# tmp / DEBUG
def _format(**kwargs):
    kwargs["date"] = kwargs["date"].strftime("%Y/%m/%d %H:%M:%S")
    # BUG: if i don't REPR the logfile, it ends up as an int ??? WTF ?
    # TODO: manage multi-line messages.
    # tag-length dependent padding or not ?
    pad = 20 * " " + " " + 11 * " " + " " + 18 * " " + "|" + " "
    return "{date} | {logfile.name:<9} | {tag:<16} | {message}\n".format(**kwargs)

# config.format = _format


