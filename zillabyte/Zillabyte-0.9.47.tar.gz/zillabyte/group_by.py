# OPERATION Group By
# PYTHON_SYNTAX
#
#  # Simple Syntax
#   stream.group_by(
#     name = "name",                            # optional
#     fields = ["field_1", "field_2", ...],
#     emits = ["stream_1", "stream_2", ...],    # optional for single output stream
#     begin_group = begin_group_function,
#     aggregate = aggregate_function,
#     end_group = end_group_function
#   )
#
#  # Expanded Syntax
#  class MyGroupBy:
#     name = "name",                            # optional
#     fields = ["field_1", "field_2", ...],
#     emits = ["stream_1", "stream_2", ...],    # optional for single output stream
#     def begin_group(self, controller, g_tuple):
#       # begin_group_function,
#     def aggregate(self, controller, tup):
#       # aggregate_function,
#     def end_group(self, controller)
#       # end_group_function
#   )# PYTHON_NOTES
#
# ### Simple Syntax
#
# The **"begin_group_function"** must take in 2 arguments (the "controller" and the "grouping tuple", which is emitted at the beginning of each group and contains the values of the fields specified in "group_by"), and should return nothing. This is where initial values for the aggregation are set.
#
# The **"aggregate_function"** must take in 2 arguments (the "controller" and the "tuple"), and should return nothing. This is where the aggregation is performed.
#
# The **"end_group_function"** must take in a single argument (the "controller"), and should return nothing. This is where the final aggregated value is emitted.
#
# ### Expanded Syntax
#
# # The **"begin_group_function"** must take in 3 arguments (the "self", the "controller" and the "grouping tuple", which is emitted at the beginning of each group and contains the values of the fields specified in "group_by"), and should return nothing. This is where initial values for the aggregation are set.
#
# The **"aggregate_function"** must take in 3 arguments (the "self",the "controller" and the "tuple"), and should return nothing. This is where the aggregation is performed.
#
# The **"end_group_function"** must take in 2 arguments (the "self", and the "controller"), and should return nothing. This is where the final aggregated value is emitted.
#
# PYTHON_EXAMPLE
#
# # Expanded Syntax
#
#  class MyGroupBy:
#
#   # The begin_function is where you initialize any state. It runs on the first tuple who's fields are unique to the operation.
#   # In this case, we save the ["word", "url"] pair we wish to count
#   def begin_group(self, controller, g_tuple):
#     self.wc_word = g_tuple["word"]
#     self.wc_url = g_tuple["url"]
#     self.wc_count = 0
#
#   # In this simple case, increment the counter
#   def word_count_aggregate_group(self, controller, tup):
#     self.wc_count += 1
#
#   # This is run after all tuples have been received for the cycle
#   # We emit the "word" , "url", and the count of the pair in tuples
#   def end_group(self, controller):
#     controller.emit({"word" : self.wc_word, "url" : self.wc_url, "count" : self.wc_count})
#
# word_stream = stream.group_by(op_class=MyGroupBy)
#
# # Simple Syntax
# # This is how the stream is actually declared
# word_stream = stream.group_by(\
#   name = "word_count",\
#   fields = ["word", "url"],\
#   begin_group = word_count_begin_group,\
#   aggregate = word_count_aggregate_group,\
#   end_group = word_count_end_group\
# )#
# # The begin_function is where you initialize any state
# # In this case, we save the ["word", "url"] pair we wish to count
# def word_count_begin_group(controller, g_tuple):
#   global wc_word
#   global wc_url
#   global wc_count
#   wc_word = g_tuple["word"]
#   wc_url = g_tuple["url"]
#   wc_count = 0
#
# # In this simple case, increment the counter
# def word_count_aggregate_group(controller, tup):
#   global wc_count
#   wc_count += 1
#
# # This is run after all tuples have been received for the cycle
# # We emit the "word" , "url", and the count of the pair in tuples
# def word_count_end_group(controller):
#   global wc_word
#   global wc_url
#   global wc_count
#   controller.emit({"word" : wc_word, "url" : wc_url, "count" : wc_count})
#
# # This is how the stream is actually declared
# word_stream = stream.group_by(\
#   name = "word_count",\
#   fields = ["word", "url"],\
#   begin_group = word_count_begin_group,\
#   aggregate = word_count_aggregate_group,\
#   end_group = word_count_end_group\
# )
import traceback
from counter import Counter
from controller import Controller, ParentDeadException
from helper import Helper
import inspect

class GroupBy:
  def __init__(self, app):
    self._app = app

  def build_node(self, *args, **kwargs):

    self._name = kwargs.pop('name', None)
    if self._name == None:
      self._name = "group_by_"+Counter.get()

    self._type = "group_by"
    self._group_by = kwargs.pop('fields', None)
    self._parallelism = kwargs.pop('parallelism', None)

    emits = kwargs.pop('emits', None)
    if emits == None:
      emits = ["stream_"+Counter.get()]
    elif isinstance(emits, basestring):
      emits = [emits]
    self._emits = emits

    # functions
    if len(args) == 1 and inspect.isclass(args[0]):
      self._class = args[0]()
      self._prepare = self._class.prepare if hasattr(self._class, "prepare") else None
      self._begin_group = self._class.begin_group if hasattr(self._class, "begin_group") else None
      self._aggregate = self._class.aggregate if hasattr(self._class, "aggregate") else None
      self._end_group = self._class.end_group if hasattr(self._class, "end_group") else None


    # check class
    Helper.check_name("group_by", self._name, self._app._names)
    Helper.check_group_by(self)
    Helper.check_emits("group_by", self._emits, self._app._streams)


  def run_operation(self):

    controller = Controller(self._emits, self._app._options)
    controller.get_pidDir()

    while True:
      try:
        d = controller.read()
        if d == None:
          continue
        elif "command" not in d:
          controller.log("Not a command "+str(d))
        elif d["command"] == "prepare":
          if self._prepare != None:
            self._prepare(controller)
        elif d["command"] == "begin_group":
          tup = controller.get_tuple(d)
          if tup == None:
            continue
          self._begin_group(controller, tup)
        elif d["command"] == "aggregate":
          tup = controller.get_tuple(d)
          if tup == None:
            continue
          self._aggregate(controller, tup)
        elif d["command"] == "end_group":
          self._end_group(controller)
        else:
          controller.log("Invalid command")
      except ParentDeadException, e:
        controller.log("jvm appears to have died")
        raise
      except KeyboardInterrupt:
        raise
      except:
        controller.fail("Exception in group_by: "+traceback.format_exc())
      controller.done()
