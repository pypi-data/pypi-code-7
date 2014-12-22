# OPERATION Each
# PYTHON_SYNTAX
# # Simple syntax:
# def execute_function(controller, tup):
#   # excute_function_code
#
# stream = stream.each(execute_function)
#
#
# # Extended Syntax
# class MyEach:
#     def prepare(self, controller):            # optional if no initialization needed
#         # prepare_function
#
#     def execute(self, controller, tup):
#         # execute_function
#
# stream = previous_stream.each(MyEach, name="name", emits=["stream_1", "stream_2"], output_format="replace")
#
# PYTHON_NOTES
# ### Simple Syntax:
#
#     The **"execute_function"** must take in 2 arguments (the "controller" and the "tuple"), and should return nothing. This is where the tuples are actually processed.
# ### Extended Syntax
# The **name** argument is optional
#
# The **emits** argument allows for emitting to specific streams
#   emits = ["stream_1", "stream_2", ...],    # optional for single output stream
#
# The allowed output formats are "replace" and "merge", defaulting to "replace"
#
#   * **"replace"** : discards the input tuple values and only emits the specified values. This is the default.
#   * **"merge"** : re-emits the input tuple values along with the specified values.
#
# The **"prepare_function"** must take in two arguments (the "self" and the "controller") and should return nothing. This is where any setup is done to prepare for tuple processing in the "execute_function". Variables can be stored by using the "self.var =" syntax.
#
# The **"execute_function"** must take in 3 arguments (the "self", the "controller" and the "tuple"), and should return nothing. This is where the tuples are actually processed. Variables set during the prepare function can be accessed here by calling the set "self.var"
# PYTHON_EXAMPLE
# from mechanize import Browser
#
# # Simple syntax
#
# # Open a url and emit the "url" and "title" fields
# def execute_basic(controller, tup):
#   url = tup["url"]
#   br = Browser()
#   br.open(url)
#   controller.emit({"url":url, "title":br.title()})
#
# # call the each
# stream = stream.each(execute_basic)
#
#
# # Extended Syntax
# class MyEach:
#
#   def prepare(self, controller):
#     self.br = Browser()
#
#   def execute(self, controller, tup):
#     url = tup["url"]
#     self.br.open(url)
#     controller.emit({"url":url, "title":self.br.title()})
#
# # call the each
# stream = stream.each(MyEach, name="my_each")
#
import traceback
from counter import Counter
from controller import Controller, ParentDeadException
from helper import Helper
import inspect

class Each:
  def __init__(self, app):
    self._app = app



  def build_node(self, *args, **kwargs):

    self._name = kwargs.pop('name', None)
    if self._name == None:
      self._name = "each_"+Counter.get()

    self._type = "each"
    self._output_format = kwargs.pop('output_format', "replace")
    self._parallelism = kwargs.pop('parallelism', None)

    emits = kwargs.pop('emits', None)
    if emits == None:
      emits = ["stream_"+Counter.get()]
    elif isinstance(emits, basestring):
      emits = [emits]
    self._emits = emits


    # functions
    op_class={}
    if len(args) == 1:
      # simple syntax
      if inspect.isfunction(args[0]):
        self._prepare = None
        self._execute = args[0]

      # extended syntax
      elif inspect.isclass(args[0]):
        self._class = args[0]()
        self._prepare = self._class.prepare if hasattr(self._class, "prepare") else None
        self._execute = self._class.execute if hasattr(self._class, "execute") else None


    # check class
    Helper.check_name("each", self._name, self._app._names)
    Helper.check_each(self)
    Helper.check_emits("each", self._emits, self._app._streams)


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
          self._execute(controller, tup)

      except KeyboardInterrupt:
        raise
      except ParentDeadException, e:
        controller.log("jvm appears to have died")
        raise
      except:
        controller.fail("Exception in each: "+traceback.format_exc())
      controller.done()
