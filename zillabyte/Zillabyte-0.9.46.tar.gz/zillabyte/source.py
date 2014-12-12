# OPERATION Source
# PYTHON_SYNTAX
# #Sourcing from a relation:
#   app.source("dataset_name")
#
# #Custom source - simple syntax:
#
# def next_tuple_function(controller):
#   # next_tuple_function
#   app.source(next_tuple_function)
#
#
# #Custom source - extended syntax:
#  Class MySource:

#     def begin_cycle(self, controller):               # optional if no initialization needed
#       # begin_cycle_function,
#
#     def next_tuple(self, controller):
#       # next_tuple_function
#
#  source = app.source(op_class=MySource, name="mysource", emits=["stream_1", "stream_2"], parallelism=2)
#
# PYTHON_NOTES
#
#
# The "end_cycle_policy" is used to specify when a cycle should end. Two options are available:
#
#   * **"null_emit"** : end the cycle when a field contains "nil" or when nothing is emitted from the "next_tuple" block.
#   * **"explicit"** : the end of a cycle is explicitly declared in the "next_tuple" block. This is done by including the "end_cycle" keyword in the "next_tuple" function, e.g. end_cycle() if queue.empty.
#
# ### Simple Syntax:
#
# The "begin_cycle_function" and "next_tuple_function" can be full functions or lambda functions.
#
#   * The **"begin_cycle_function"** must take in a single argument (the "controller") and should return nothing. This is where any setup is done to initialize the content and quantity of tuples emitted by "next_tuple_function".
#   * The **"next_tuple_function"** must take in one argument (the "controller" and ), and should return nothing. This is where the tuples are actually emitted.
#
# ### Extended Syntax:
#
#   * The **"begin_cycle_function"** must take in a two arguments argument (the "self" and the "controller") and should return nothing. This is where any setup is done to initialize the content and quantity of tuples emitted by "next_tuple_function".
#   * The **"next_tuple_function"** must take in 2 arguments (the "self" and the "controller" ), and should return nothing. This is where the tuples are actually emitted.
#
#   The **name** argument is optional and is passed inline
#   The **emits** function allows you to specific the streams for output, and is optional
#     emits = ["stream_1", "stream_2", ...],
#
##  PYTHON_EXAMPLE
# # Source from the "homepages" relation
# stream = app.source(matches = "homepages")
#
#
#
# # Custom Source - Simple Syntax
# source_pages = ["http://www.zillabyte.com", "http://docs.zillabyte.com", "http://www.zillabyte.com/about", "http://blog.zillabyte.com"]
#
# def nt(controller):
#   if(len(source_pages) > 0):
#     controller.emit({"url":source_pages.pop(0)})
#   else:
#     controller.end_cycle()
#
# app = zillabyte.app(name = "python_app")
#
# stream = app.source(nt)
#
# # Custom Source - Extended Syntax
#
# class MySource:
#   def begin_cycle(self,controller):
#     self.source_pages = "http://www.zillabyte.com", "http://docs.zillabyte.com", "http://www.zillabyte.com/about", "http://blog.zillabyte.com"]
#
#   def next_tuple(self, controller):
#     if(len(self.source_pages) > 0):
#       controller.emit({"url":self.source_pages.pop(0)})
#     else:
#       controller.end_cycle()
#
# app = zillabyte.app(name = "python_app")
#
# stream = app.source(MySource, name="mysource", end_cycle_policy="explicit")
import traceback
from counter import Counter
from controller import Controller, ParentDeadException, UserEndCycleException
from helper import Helper
import inspect

class Source:
  def __init__(self, app):
    self._app = app


  def build_node(self, *args, **kwargs):

    self._name = kwargs.pop('name', None)
    if self._name == None:
      self._name = "source_"+Counter.get()

    self._type = "source"
    self._options = kwargs.pop('options', {})
    self._matches = None
    self._relation = None
    self._end_cycle_policy = kwargs.pop('end_cycle_policy', "null_emit")

    emits = kwargs.pop('emits', None)
    if emits == None:
      emits = ["stream_"+Counter.get()]
    elif isinstance(emits, basestring):
      emits = [emits]
    self._emits = emits


    # functions
    self._begin_cycle = None
    self._prepare = None
    self._next_tuple = None

    if len(args) == 1:

      # source from relation
      if isinstance(args[0], basestring):
        matches = args[0]
        Helper.check_matches(matches)
        if not isinstance(self._options, dict):
          self._options = {}
        self._relation = {"query": matches, "options": self._options}
        self._matches = matches

      # simple syntax
      elif inspect.isfunction(args[0]):
        self._next_tuple = args[0]

      # extended syntax
      elif inspect.isclass(args[0]):
        self._class = args[0]()
        self._prepare = self._class.prepare if hasattr(self._class, "prepare") else None
        self._begin_cycle = self._class.begin_cycle if hasattr(self._class, "begin_cycle") else None
        self._next_tuple = self._class.next_tuple if hasattr(self._class, "next_tuple") else None


    # check the operation
    Helper.check_name("source", self._name, self._app._names)
    Helper.check_source(self)
    Helper.check_emits("source", self._emits, self._app._streams)



  def run_operation(self):

    controller = Controller(self._emits, self._app._options)
    controller.get_pidDir()

    while True:
      try:
        d = controller.read()
        if d == None:
          continue
        elif "command" not in d:
          controller.log("Not a command")
        elif d["command"] == "prepare":
          if self._prepare != None:
            self._prepare(controller)
        elif d["command"] == "begin_cycle":
          if(self._begin_cycle != None):
            self._begin_cycle(controller)
        elif d["command"] == "next":
            self._next_tuple(controller)
        elif d["command"] == "ack":
          controller.ack(d.get("id",None))
        elif d["command"] == "fail":
          controller.fail(d.get("id",None))
        else:
          controller.log("Invalid command")
      except UserEndCycleException, e:
        pass
      except KeyboardInterrupt:
        raise
      except ParentDeadException, e:
        controller.log("jvm appears to have died")
        raise
      except:
        controller.fail("Exception in source: "+traceback.format_exc())
      controller.done()
