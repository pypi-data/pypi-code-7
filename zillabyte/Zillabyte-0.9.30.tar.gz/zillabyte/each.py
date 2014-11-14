# OPERATION Each
# LANGUAGE_SYNTAX 
# stream.each( name = "name", \t\t\t\t => optional
#              emits = ["stream_1", "stream_2", ...], \t => optional for single output stream
#              output_format = "replace" OR "merge", \t => optional, defaults to "replace"
#              prepare = prepare_function, \t\t => optional if no initialization needed
#              execute = execute_function )
# - The allowed output formats are "replace" and "merge".
#     * "replace" - discards the input tuple values and only emits the specified values. This is the default.
#     * "merge" - re-emits the input tuple values along with the specified values.
# - The "prepare_function" must take in a single argument (the "controller") and should return nothing. This is where any setup is done to prepare for tuple processing in the "execute_function".
# - The "execute_function" must take in 2 arguments (the "controller" and the "tuple"), and should return nothing. This is where the tuples are actually processed."""
#  
# EXAMPLE 
# from mechanize import Browser
#  
# br = None
# def prep(controller):
#   global br
#   br = Browser()
#  
# # Open a url and emit the "url" and "title" fields
# def ee(controller, tup):
#   global br
#   url = tup["url"]
#   br.open(url)
#   controller.emit({"url":url, "title":br.title()})
#  
# stream = stream.each(name="test_python", prepare=prep, execute=ee)
import traceback
from counter import Counter
from controller import Controller, ParentDeadException
from helper import Helper

class Each:
  def __init__(self, app):
    self._app = app

  def build_node(self, name, emits, output_format, prepare, execute, parallelism):
    self._name = name if name else "each_"+Counter.get()
    self._type = "each"
    self._output_format = output_format

    if emits == None:
      emits = ["stream_"+Counter.get()]
    elif isinstance(emits, basestring):
      emits = [emits]
    self._emits = emits

    self._prepare = prepare
    self._execute = execute
    self._parallelism = parallelism

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
