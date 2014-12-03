# OPERATION Clump
# PYTHON_SYNTAX 
# # Simplified syntax:
# stream.clump(execute=execute_function)
#
# # Expanded Syntax
# class MyClump:
#     name = "name"                            # optional
#     size = 100                               # optional, defaults to 100
#     emits = ["stream_1", "stream_2", ...]    # optional for single output stream
#     output_format = "replace" OR "merge",    # optional, defaults to "replace"
# 
#     def prepare(self, controller):           # optional if no initialization needed
#       # prepare_function...
# 
#     def execute(self, controller, tuples):
#       # execute_function...\
# 
# stream = stream.clump(op_class=MyClass)
#
# PYTHON_NOTES 
# The `size` parameter is optional.  It is the target size of the clump.  The system is guaranteed to not exceed `size`, but there are no guarantees about smaller clumps. If no `size` is given, then 100 is default.
# 
# The simplified syntax can be used if a prepare block and other customizations are not needed.
# 
#   * **Note:** this syntax only works for a single output stream.
#  
# The allowed output formats are :replace and :merge.
#
#   * **:replace** : discards the input tuple values and only emits the specified values. This is the default.
#   * **:merge** : re-emits the input tuple values along with the specified values.
#  
# The "prepare" and "execute" blocks can be passed as functions or defined within the class
#
#   * **"prepare"** block : where any setup is done to prepare for tuple processing in the "execute" block.
#   * **"execute"** block : where the tuples are actually processed. It must take in a single argument (the "tuple").
# 
# PYTHON_EXAMPLE 
#  
# # Sink data into an external sql database 
# class MyClump:
#   size = 50
#   def execute(self, controller, tuples)
#     values = ', '.join(map(lambda t: t['value'], tuples))
#     sql = "INSERT INTO table VALUES " + values
#     @my_sql_service.execute(sql)
#  
# stream.clump(op_class=MyClump)
#  
import traceback
from counter import Counter
from controller import Controller, ParentDeadException
from helper import Helper
class Clump:
  def __init__(self, app):
    self._app = app

  def build_node(self, **kwargs):

    self._name = kwargs.pop('name', None)
    if self._name == None:
      self._name = "clump_"+Counter.get()    

    self._type = "clump"
    self.size = kwargs.pop("size", 100)
    self._output_format = kwargs.pop('output_format', "replace")
    self._parallelism = kwargs.pop('parallelism', None)

    emits = kwargs.pop('emits', None)
    if emits == None:
      emits = ["stream_"+Counter.get()]
    elif isinstance(emits, basestring):
      emits = [emits]
    self._emits = emits

    # functions
    prepare = kwargs.pop('prepare', None)
    execute = kwargs.pop('execute', None)


    is_class = kwargs.pop('class', None)
    if is_class:
      self._prepare = lambda controller: prepare(self, controller)
      self._execute = lambda controller, tuples: execute(self, controller, tuples)
    else:
      self._prepare = prepare
      self._execute = execute


    # add any user created variables or helpers
    for key, value in kwargs.iteritems():
      self.key = value

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
          tuples = controller.get_tuples(d)
          if tuples == None:
            continue
          self._execute(controller, tuples)

      except KeyboardInterrupt:
        raise
      except ParentDeadException, e:
        controller.log("jvm appears to have died")
        raise
      except:
        controller.fail("Exception in each: "+traceback.format_exc())
      controller.done()
