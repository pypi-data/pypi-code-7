# OPERATION Filter
# PYTHON_SYNTAX

# # Simple Syntax
#
#  def keep_function(tup):
#    # keep_function
#
#  stream = stream.filter(keep_function)
#
#
#  Extended Syntax
#
#  class MyFilter:
#    def prepare(self, controller):
#      # prepare function
#
#    def keep(self, tup):
#      # keep_function
#
#  stream = stream.filter(MyFilter, name = "name", emits = "stream")
# PYTHON_NOTES
# A "filter" may only emit a single stream.
# ### Simple Syntax:
#
#  The simple syntax allows for a simple filter to run over incoming tuples
#
#  The **"keep_function"** can be a full function or a lambda function. It must take in a single argument (the tuple), and return boolean "True" or "False". Tuples will pass through if "keep_function" returns "True".
# ### Extended Syntax
#
# A Filter class is instantiated with the **keep** and optional **prepare** methods
#
# The **"prepare_function"** must take in two arguments (the "self" and the "controller") and should return nothing. This is where any setup is done to prepare for tuple processing in the "keep" function. Variables can be stored by using the "self.var =" syntax.
#
# The **"keep_function"** must take in 2 arguments (the "self" and the tuple "tup"), and return boolean "True" or "False". Tuples will pass through if "keep_function" returns "True".
#
# The **name** keyword argument is optional and allows you to name the stream
#
# The **emits** keyword argument is optional and allows you to declare a single stream(**emits="stream_a"**), or multiple streams(**emits=["stream_a", "stream_b"]) for output
#
# PYTHON_EXAMPLE
#
# # Simple Syntax
# # Checks for tuples whose "url" field begin with "https"
# def keep_https(tup):
#   return tup["url"].starts_with("https")
#
# stream = stream.filter(keep_keep_https)
# Expanded Syntax
#
# class MyFilter:
#   name = "https_filter"
#   def keep(self,, tup)
#     return tup["url"].starts_with("https")
#
# stream = stream.filter(MyFilter)
#
import traceback
from counter import Counter
from controller import Controller, ParentDeadException
from helper import Helper
import inspect

class Filter:
  def __init__(self, app):
    self._app = app

  def build_node(self,*args, **kwargs):

    self._name = kwargs.pop('name', None)
    if self._name == None:
      self._name = "filter_"+Counter.get()

    self._type = "filter"
    self._parallelism = kwargs.pop('parallelism', None)

    emits = kwargs.pop('emits', None)
    if emits == None:
      emits = ["stream_"+Counter.get()]
    elif isinstance(emits, basestring):
      emits = [emits]
    self._emits = emits

    # functions
    prepare = kwargs.pop("prepare", None)
    keep = kwargs.pop('keep', None)

    is_class = kwargs.pop("class", None)
    if is_class:
      self._prepare = lambda controller: prepare(self, controller)
      self._keep = lambda tup: keep(self, tup)
    else:
      self._prepare = prepare
      self._keep = keep

    # functions
    op_class={}
    if len(args) == 1:
      # simple syntax
      if inspect.isfunction(args[0]):
        self._prepare = None
        self._keep = args[0]

      # extended syntax
      elif inspect.isclass(args[0]):
        self._class = args[0]()
        self._prepare = self._class.prepare if hasattr(self._class, "prepare") else None
        self._keep = self._class.keep if hasattr(self._class, "keep") else None


    Helper.check_name("filter", self._name, self._app._names)
    Helper.check_filter(self)
    Helper.check_emits("filter", self._emits, self._app._streams)

  def run_operation(self):

    controller = Controller(self._emits, self._app._options)
    controller.get_pidDir()

    while True:
      try:
        d = controller.read()
        if d == None:
          continue
        elif "command" in d and d["command"] == "prepare":
          if self._prepare != None:
            self._prepare(controller)
        else:
          tup = controller.get_tuple(d)
          if tup == None:
            continue
          keep = self._keep(tup)
          if keep:
            controller.emit(tup)
      except KeyboardInterrupt:
        raise
      except ParentDeadException, e:
        controller.log("jvm appears to have died")
        raise
      except:
        controller.fail("Exception in filter: "+traceback.format_exc())
      controller.done()
