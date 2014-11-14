# OPERATION Source
# LANGUAGE_SYNTAX 
#   Sourcing from a relation:
#     app.source( matches = "SQL query" or [SXP queries] )
# 
#   Custom source:
#     app.source( name = "name", \t\t\t\t\t => optional
#                 emits = ["stream_1", "stream_2", ...], \t\t => optional for single output stream
#                 end_cycle_policy = "null_emit" OR "explicit", \t => default "null_emit"
#                 begin_cycle = begin_cycle_function, \t\t => optional if no initialization needed
#                 next_tuple = next_tuple_function )
# 
#   - The "end_cycle_policy" is used to specify when a cycle should end. Two options are available:
#       * :null_emit - end the cycle when a field contains "nil" or when nothing is emitted from the "next_tuple" block.
#       * :explicit - the end of a cycle is explicitly declared in the "next_tuple" block. This is done by including the "end_cycle" keyword in the "next_tuple" function, e.g. end_cycle() if queue.empty.
#   - The "begin_cycle_function" and "next_tuple_function" can be full functions or lambda functions. 
#       * "begin_cycle_function" must take in a single argument (the "controller") and should return nothing. This is where any setup is done to initialize the content and quantity of tuples emitted by "next_tuple_function".
#       * "next_tuple_function" must take in 2 arguments (the "controller" and the "tuple"), and should return nothing. This is where the tuples are actually emitted."""
# EXAMPLE 
# # Source from the "homepages" relation
# stream = app.source(name="homepages")
#  
#  
#  
# # Custom Source
# source_pages = ["http://www.zillabyte.com", "http://docs.zillabyte.com", "http://www.zillabyte.com/about", "http://blog.zillabyte.com"]
#  
# def nt(controller):
#   if(len(source_pages) > 0):
#     controller.emit({"url":source_pages.pop(0)})
#   else:
#     controller.end_cycle()
#  
# app = zillabyte.app(name="python_app")
#  
# stream = app.source(name="python_source", next_tuple=nt, end_cycle_policy="explicit")
import traceback
from counter import Counter
from controller import Controller, ParentDeadException, UserEndCycleException
from helper import Helper

class Source:
  def __init__(self, app):
    self._app = app

  def build_node(self, name, matches, options, emits, end_cycle_policy, prepare, begin_cycle, next_tuple):
    self._name = name if name else "source_"+Counter.get()
    self._type = "source"
    self._options = options
    self._matches = None
    self._relation = None
    self._end_cycle_policy = None

    if(matches != None):
      Helper.check_matches(matches)
      if isinstance(matches, basestring):
        if not isinstance(options, dict):
          options = {}
        self._relation = {"query": matches, "options": options}
      elif isinstance(matches, list):
        self._matches = matches
    else:
      self._end_cycle_policy = end_cycle_policy

    if emits == None:
      emits = ["stream_"+Counter.get()]
    elif isinstance(emits, basestring):
      emits = [emits]
    self._emits = emits

    self._prepare = prepare
    self._begin_cycle = begin_cycle
    self._next_tuple = next_tuple

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
