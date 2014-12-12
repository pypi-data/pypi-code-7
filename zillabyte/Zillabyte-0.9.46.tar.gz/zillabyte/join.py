# OPERATION Join
# PYTHON_SYNTAX
#   lhs_stream.join_with(\
#     rhs_stream,                                                       # the stream to join on
#     name = "name",                                                   # optional
#     stream = rhs_stream_object,
#     fields = "join_field" OR ["lhs_join_field", "rhs_join_field"],
#     emits = "stream",                                                # optional
#     options = {options}
#   )
# PYTHON_NOTES
# A "join" may only emit a single stream.
#
# The following options can be used in a join:
#
# Mandatory:
#
#  * **"fields"** : specifies the fields to join on. The value must be a STRING or a length-2 ARRAY. If value = a STRING, the LH and RH join fields will both be set to this STRING. If value = a length-2 ARRAY, the LH join field will be set to array[0] and the RH join field will be set to array[1].
#
# Optional:
#
#  * **"type"** : specifies the join type. The default is "left". Options are ["inner", "outer", "left", "right"]
#  * **"emits"** : specifies the stream to emit. A "join" may only emit a single stream.
#
# PYTHON_EXAMPLE
#
# word_stream = employee_stream.join_with(\
#   budget_stream, \
#   name = "join",\
#   fields = ["occupation", "number"],\
#   options = {"type" : "left"}\
# )
from counter import Counter
from helper import Helper
class Join:
  def __init__(self, app):
    self._app = app

  def build_node(self, **kwargs):
    name = kwargs.pop("name", None)
    if name:
      self._name = name
    else:
      self._name = "join_"+Counter.get()

    self._type = "join"
    self._lhs_stream = kwargs.pop("lhs_stream")._name
    self._rhs_stream = kwargs.pop("rhs_stream")._name

    emits = kwargs.pop("emits", None)
    if emits == None:
      emits = ["stream_"+Counter.get()]
    elif isinstance(emits, basestring):
      emits = [emits]
    self._emits = emits

    fields = kwargs.pop("fields", None)
    if fields:
      if isinstance(fields, list) and len(fields) == 2:
        self._lhs_fields = fields[0]
        self._rhs_fields = fields[1]
      elif isinstance(fields, basestring):
        self._lhs_fields = fields
        self._rhs_fields = fields

    self._join_type = "inner"
    options = kwargs.pop("options", None)
    if options:
      if options["type"]:
        self._join_type = options["type"]

    Helper.check_name("join", self._name, self._app._names)
    Helper.check_join(self)
    Helper.check_emits("join", self._emits, self._app._streams)

  def run_operation(self):
    print "Joins can only be instantiated on our cluster, sorry!"
