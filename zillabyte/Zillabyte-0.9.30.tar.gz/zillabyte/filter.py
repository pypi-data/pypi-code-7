# OPERATION Filter
# LANGUAGE_SYNTAX 
# "Filter" Syntax:
#   stream.filter( name = "name", \t\t\t\t => optional
#                  emits = "stream", \t\t\t\t => optional
#                  prepare = prepare_function, \t => optional if no initialization needed
#                  keep = keep_function )
#   - A "filter" may only emit a single stream.
#   - The "prepare_function" must take in a single argument (the "controller") and should return nothing. This is where any setup is done to prepare for tuple processing in the "keep_function".
#   - The "keep_function" can be a full function or a lambda function. It must take in a single argument (the tuple), and return boolean "True" or "False". Tuples will pass through if "keep_function" returns "True"."""
# EXAMPLE 
# # Checks for tuples whose "url" field begin with "https"
# def keep_https(tuple):
#   return tuple["url"].starts_with("https")
#  
# stream = stream.filter(
#   name = "https_filter",
#   keep = keep_keep_https
# )
# 
import traceback
from counter import Counter
from controller import Controller, ParentDeadException
from helper import Helper

class Filter:
  def __init__(self, app):
    self._app = app

  def build_node(self, name, emits, prepare, keep, parallelism):
    self._name = name if name else "filter_"+Counter.get()
    self._type = "filter"

    if emits == None:
      emits = ["stream_"+Counter.get()]
    elif isinstance(emits, basestring):
      emits = [emits]
    self._emits = emits

    self._prepare = prepare
    self._keep = keep
    self._parallelism = parallelism

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
          if self._keep(tup):
            controller.emit(tup)
      except KeyboardInterrupt:
        raise
      except ParentDeadException, e:
        controller.log("jvm appears to have died")
        raise
      except:
        controller.fail("Exception in filter: "+traceback.format_exc())
      controller.done()
