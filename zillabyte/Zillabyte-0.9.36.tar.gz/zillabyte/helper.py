import re
import sys
import json

class Helper:

  META_NAMES = ["id", "confidence", "since", "source"]
  ALLOWED_END_CYCLE_POLICIES= ["null_emit", "explicit"]
  ALLOWED_OUTPUT_FORMATS = ["replace", "merge"]
  ALLOWED_TYPES = ["string", "integer", "float", "double", "boolean", "array", "map"]
 
  argv = sys.argv[1:]
  @classmethod
  def set_argv(self, v):
    self.argv = v

  @classmethod  
  def opt_parser(self):
    options = {}
    i = 0
    while(i < len(self.argv)):
      arg = self.argv[i]
      if arg == "--execute_live":
        options["command"] = "execute"
      elif arg == "--info":
        options["command"] = "info"
      elif arg == "--name":
        i += 1
        options["name"] = self.argv[i]
      elif arg == "--unix_socket":
        i += 1
        options["unix_socket"] = self.argv[i]
      elif arg == "--host":
        i += 1
        options["host"] = self.argv[i]
      elif arg == "--port":
        i += 1
        options["port"] = self.argv[i]
      i += 1
    return options
  
  @classmethod
  def print_error(self, msg):
    sys.stderr.write(msg+"\n")
    sys.exit(1)
 
  @classmethod
  def write_hash_to_file(self, h, f):
    f.write(json.dumps(h)+"\n")
    f.flush()

  @classmethod
  def write_node_to_file(self, h, f):
    self.write_hash_to_file({"class":"node", "info":h},f)

  @classmethod
  def write_arc_to_file(self, h, f):
    self.write_hash_to_file({"class":"arc", "info":h},f)
 
  @classmethod
  def check_name(self, operation, name, names):
    ee = "Error in \"%s\" at \"name\": \n\t " % (operation)
  
    if not isinstance(name, basestring) or re.match('^[\w]+$', name) == None:
      msg = ee+"\"Name\" must be a non-empty STRING with only alphanumeric and underscore characters at %s. Apps and components must have names. The following methods must have names as well: \"sink\", \"inputs\" and \"outputs\"."%(str(name))
      self.print_error(msg)

    # sink duplicate names are checked on their own
    if name in names and names[name] != "app" and names[name] != "sink" and operation != "app" and operation != "sink":
      msg = ee+"The \"name\" \"%s\" was previously defined in a %s!"%(name, names[name])
      self.print_error(msg)
    names[name] = operation

    if re.match('^[0-9]$', name[0]) != None:
      msg = ee+"The \"name\" \"%s\" cannot begin with a number."%(name)
      self.print_error(msg)

  @classmethod
  def check_matches(self, matches):
    ee = "Error in \"source\" at \"matches\": \n\t "
    pp = self.print_check_source

    if((not isinstance(matches, basestring)) and (not isinstance(matches, list))):
      msg = ee+"Invalid \"matches\" argument. When sourcing from a relation, please specify an SQL query-string or SXP query-array in \"matches\"."+pp
      self.print_error(msg)

  @classmethod
  def check_emits(self, operation, emits, streams):
    if operation == "component":
      oo = "outputs"
    else:
      oo = "emits"
    ee = "Error in \"%s\" at \"%s\": \n\t "%(oo,operation)

    if(not isinstance(emits, list)):
      msg = ee+"The \"%s\" must be a LIST."%(oo)
      self.print_error(msg)

    for e in emits:
      if not isinstance(e, basestring) or re.match('^[\w]+$', e) == None:
        msg = ee+"An \"%s\" stream name must be a non-empty STRING with only alphanumeric and underscore characters in %s."%(oo,str(e))
        self.print_error(msg)
      if e in streams:
        msg = ee+"The stream name \"%s\" is previously defined!"%(e)
        self.print_error(msg)
      streams[e] = operation

  @classmethod
  def check_output_format(self, operation, output_format):
    ee = "Error in \"%s\" at \"output_format\": \n\t "%(operation)

    if not output_format in self.ALLOWED_OUTPUT_FORMATS:
      msg = ee+"Invalid \"output_format\": \"%s\". The allowed formats are \"replace\" and \"merge\"."%(output_format)
      self.print_error(msg)

  @classmethod
  def check_source(self, node):
    ee = "Error in \"source\": \n\t "
    pp = self.print_check_source

    rm = True if node._relation else False
    mm = True if node._matches else False

    if((rm or mm) and (node._begin_cycle != None or node._next_tuple != None)):
      msg = ee+"A \"source\" cannot contain a \"matches\" argument as well as \"begin_cycle\" or \"next_tuple\" arguments."+pp
      self.print_error(msg)

    if(node._end_cycle_policy and not (node._end_cycle_policy in self.ALLOWED_END_CYCLE_POLICIES)):
      msg = ee+"Invalid \"end_cycle_policy\": \"%s\". The allowed policies are :null_emit and :explicit."%(node._end_cycle_policy)+pp
      self.print_error(msg)

    if((not rm) and (not mm) and (not node._next_tuple)):
      msg = ee+"A \"source\" must contain a valid \"matches\" argument or a \"next_tuple\" argument."+pp
      self.print_error(msg)
 
  @classmethod
  def check_each(self, node):
    ee = "Error in \"each\": \n\t "
    pp = self.print_check_each

    if (node._parallelism != None and not (type(node._parallelism) is int and node._parallelism > 0)):
      msg = "Parallelism for \"each\" must be positive integer" 
      self.print_error(msg)

    if(node._execute == None):
      msg = ee+"An \"each\" must contain an \"execute\" function."+pp
      self.print_error(msg)

    self.check_output_format("each", node._output_format)

  @classmethod
  def check_filter(self, node):
    ee = "Error in \"filter\": \n\t "
    pp = self.print_check_filter

    if(len(node._emits) != 1):
      msg = ee+"A \"filter\" must emit a single stream. %s"%(node._emits)+pp
      self.print_error(msg)

    if (node._parallelism != None and not (type(node._parallelism) is int and node._parallelism > 0)):
      msg = "Parallelism for \"each\" must be positive integer" 
      self.print_error(msg)

    if(node._keep == None):
      msg = ee+"A \"filter\" must contain a \"keep\" function."+pp
      self.print_error(msg)

  @classmethod
  def check_group_by(self, node):
    ee = "Error in \"group_by\": \n\t "
    pp = self.print_check_group_by

    if(node._group_by == None or node._group_by == []):
      msg = ee+"A \"group_by\" must contain a non-empty \"group_by\" clause."+pp
      self.print_error(msg)
    for field in node._group_by:
      if not isinstance(field, basestring) or re.match('^[\w]+$', field) == None:
        msg = ee+"Field names must be non-empty STRINGS with only alphanumeric and underscore characters at \"%s\"."%(field)+pp
        self.print_error(msg)

    if(node._begin_group == None):
      msg = ee+"A \"group_by\" must contain a \"begin_group\" function."+pp
      self.print_error(msg)
    if(node._aggregate == None):
      msg = ee+"A \"group_by\" must contain an \"aggregate\" function."+pp
      self.print_error(msg)
    if(node._end_group == None):
      msg = ee+"A \"group_by\" must contain an \"end_group\" function."+pp
      self.print_error(msg)

  @classmethod
  def check_join(self, node):
    ee = "Error in \"join_with\": \n\t "
    pp = self.print_check_join

    if len(node._emits) != 1:
      msg = ee+"A \"join_with\" must emit a single stream."+pp
      self.print_error(msg)

    lhs_fields = getattr(node, "_lhs_fields", None)
    rhs_fields = getattr(node, "_rhs_fields", None)
    if lhs_fields == None or rhs_fields == None:
      msg = ee+"The fields to join on must be specified in the format described below!"+pp
      self.print_error(msg)
    if not isinstance(lhs_fields, basestring) or re.match('^[\w]+$', lhs_fields) == None:
      msg = ee+"Field names must be non-empty STRINGS with only alphanumeric and underscore characters at \"%s\"."%(lhs_fields)+pp
      self.print_error(msg)
    if not isinstance(rhs_fields, basestring) or re.match('^[\w]+$', rhs_fields) == None:
      msg = ee+"Field names must be non-empty STRINGS with only alphanumeric and underscore characters at \"%s\"."%(rhs_fields)+pp
      self.print_error(msg)

    supported_joins = ["inner", "left", "right"]
    if node._join_type not in supported_joins:
      msg = ee+"The requested \"join_type\", \"%s\", is not supported. Currently we support \"%s\"."%(node._join_type, str(supported_joins))+pp
      self.print_error(msg)

  @classmethod
  def check_call_component(self, node):
    ee = "Error in \"call_component\": \n\t "
    pp = self.print_check_call_component

    idn = node._id
    if idn == None:
      msg = ee+"The \"component_id\" must be specified. This may be the name or ID of the component. Check \"zillabyte components\" to find this information."+pp
      self.print_error(msg)

    # \w matchs [0-9]
    if not isinstance(idn, basestring) or re.match('^[\w]+$', idn) == None:
      msg = ee+"The \"component_id\" must be a non-empty STRING with only alphanumeric and underscore characters in \"%s\"."%(idn)+pp
      self.print_error(msg)

    self.check_output_format("call_component", node._output_format)

  @classmethod
  def check_sink(self, name, columns, nodes, operation):
    ee = "Error in \"%s\": \n\t "%(operation)
    if operation == "sink":
      pp = self.print_check_sink
    elif operation == "outputs":
      pp = self.print_check_component_sink
  
    if not name:
      msg = ee+"Relation name must be specified!"+pp
      self.print_error(msg)
    self.check_name(operation, name, {})
  
    if len(columns) == 0:
      msg = ee+"Must be at least one output field to relation \"%s\"."%(name)+pp
      self.print_error(msg)
    self.check_field_format(operation, pp, name, columns)
  
    for node in nodes:
      if node._type != "sink":
        continue
      if node._name == name and node._columns != columns:
        msg = ee+"The relation \"%s\" has already been specified and contains a different set of fields/types."%(name)+pp
        self.print_error(msg)
  
  @classmethod
  def check_field_format(self, operation, pp, name, columns):
    ee = "Error in \"%s\": \n\t "%(operation)
  
    if not isinstance(columns, list):
      msg = ee+"Field names must be a LIST of DICTIONARIES in \"%s\"."%(name)+pp
      self.print_error(msg)
    for col in columns:
      if not isinstance(col, dict):
        msg = ee+"Field names must be listed in DICTIONARY format in \"%s\"."%(name)+pp
        self.print_error(msg)
      colkeys = col.keys()
      if len(colkeys) != 1:
        msg = ee+"Each field must be a separate DICTIONARY with {field_name : data_type} in \"%s\"."%(name)+pp
        self.print_error(msg)
      colkey = colkeys[0]
      if not isinstance(colkey, basestring) or re.match('^[\w]+$', colkey) == None :
        msg = ee+"Field names must be non-empty STRINGS in \"%s\"."%(name)+pp
        self.print_error(msg)
      if(re.match('^v[0-9]+$', colkey) != None or colkey in self.META_NAMES):
        msg = ee+"\"v[number]\", \"id\", \"confidence\", \"since\" and \"source\" are special names in Zillabyte. Please name your field something else."+pp
        self.print_error(msg)
      colval = col[colkey]
      if not isinstance(colval, basestring) or colval == "":
        msg = ee+"Field data types must be non-empty STRINGS in \"%s\"."%(name)+pp
        self.print_error(msg)
      if colval not in self.ALLOWED_TYPES:
        msg = ee+"Invalid field data type at \"%s\" in \"%s\"."%(colval,name)+pp
        self.print_error(msg)

  @classmethod
  def check_component_source(self, node):
    ee = "Error in \"inputs\": \n\t "
    pp = self.print_check_component_source

    self.check_field_format("inputs", pp, node._name, node._fields)
  
  @classmethod
  def check_component_sink(self, node):
    ee = "Error in \"outputs\": \n\t "
    pp = self.print_check_component_sink

    self.check_field_format("outputs", pp, node._name, node._columns)

  @classmethod
  def check_loop_back(self, stream, node_name, max_iterations, nodes):
    ee = "Error in \"loop_back\" to \"%s\": \n\t "%(node_name)
    pp = self.print_check_loop_back

    if max_iterations != None and not isinstance(max_iterations, int):
      msg = ee+"Max iterations must be an integer."+pp
      self.print_error(msg)

    previous_node_name = stream._previous_node_name
    found = False
    for node in nodes:
      if node._name == node_name:
        found = True
        if node._type == "source":
          msg = ee+"Cannot loop back to source node \"%s\"!"%(node_name)+pp
          self.print_error(msg)
      if node._name == previous_node_name:
        if len(node._emits) < 2:
          msg = ee+"The preceding operation does not emit multiple streams. Please make sure that it emits one stream for the loop back and another stream for downstream operations."+pp
          self.print_error(msg)
    if not found:
      msg = ee+"The specified loop-back node \"%s\" was not found in the operations preceding it."%(node_name)+pp
      self.print_error(msg)

  print_check_source = """\n
"Source" Syntax:
  Sourcing from a relation:
    app.source( matches = "SQL query" or [SXP queries] )

  Custom source:
    app.source( name = "name", \t\t\t\t\t => optional
                emits = ["stream_1", "stream_2", ...], \t\t => optional for single output stream
                end_cycle_policy = "null_emit" OR "explicit", \t => default "null_emit"
                begin_cycle = begin_cycle_function, \t\t => optional if no initialization needed
                next_tuple = next_tuple_function )

  - The "end_cycle_policy" is used to specify when a cycle should end. Two options are available:
      * :null_emit - end the cycle when a field contains "nil" or when nothing is emitted from the "next_tuple" block.
      * :explicit - the end of a cycle is explicitly declared in the "next_tuple" block. This is done by including the "end_cycle" keyword in the "next_tuple" function, e.g. end_cycle() if queue.empty.
  - The "begin_cycle_function" and "next_tuple_function" can be full functions or lambda functions. 
      * "begin_cycle_function" must take in a single argument (the "controller") and should return nothing. This is where any setup is done to initialize the content and quantity of tuples emitted by "next_tuple_function".
      * "next_tuple_function" must take in 2 arguments (the "controller" and the "tuple"), and should return nothing. This is where the tuples are actually emitted."""

  print_check_each = """\n
"Each" Syntax:
  stream.each( name = "name", \t\t\t\t => optional
               emits = ["stream_1", "stream_2", ...], \t => optional for single output stream
               output_format = "replace" OR "merge", \t => optional, defaults to "replace"
               prepare = prepare_function, \t\t => optional if no initialization needed
               execute = execute_function )
  - The allowed output formats are "replace" and "merge".
      * "replace" - discards the input tuple values and only emits the specified values. This is the default.
      * "merge" - re-emits the input tuple values along with the specified values.
  - The "prepare_function" must take in a single argument (the "controller") and should return nothing. This is where any setup is done to prepare for tuple processing in the "execute_function".
  - The "execute_function" must take in 2 arguments (the "controller" and the "tuple"), and should return nothing. This is where the tuples are actually processed."""

  print_check_filter = """\n
"Filter" Syntax:
  stream.filter( name = "name", \t\t\t\t => optional
                 emits = "stream", \t\t\t\t => optional
                 prepare = prepare_function, \t => optional if no initialization needed
                 keep = keep_function )
  - A "filter" may only emit a single stream.
  - The "prepare_function" must take in a single argument (the "controller") and should return nothing. This is where any setup is done to prepare for tuple processing in the "keep_function".
  - The "keep_function" can be a full function or a lambda function. It must take in a single argument (the tuple), and return boolean "True" or "False". Tuples will pass through if "keep_function" returns "True"."""

  print_check_group_by = """\n
"Group By" Syntax:
  stream.group_by( name = "name", \t\t\t\t => optional
                   fields = ["field_1", "field_2", ...],
                   emits = ["stream_1", "stream_2", ...], \t => optional for single output stream
                   begin_group = begin_group_function
                   aggregate = aggregate_function
                   end_group = end_group_function )
  - The "begin_group_function" must take in 2 arguments (the "controller" and the "grouping tuple", which is emitted at the beginning of each group and contains the values of the fields specified in "group_by"), and should return nothing. This is where initial values for the aggregation are set.
  - The "aggregate_function" must take in 2 arguments (the "controller" and the "tuple"), and should return nothing. This is where the aggregation is performed.
  - The "end_group_function" must take in a single argument (the "controller"), and should return nothing. This is where the final aggregated value is emitted."""

  print_check_join = """\n
"Join" Syntax:
  lhs_stream.join_with( name = "name", \t\t\t\t\t\t\t\t => optional
                        stream = rhs_stream_object,
                        fields = "join_field" OR ["lhs_join_field", "rhs_join_field"],
                        emits = "stream", \t\t\t\t\t\t\t => optional
                        options = {options} )
  - A "join" may only emit a single stream.
  - The following options are supported:
      * "type" \t -- specifies the join type. The default is "inner".
"""

  print_check_sink = """\n
"Sink" Syntax:
  stream.sink( name = "relation_name",
               columns = [{"field_1" : "type_1"}, {"field_2" : "type_2"}, ...] )
  - "Sink" relation "name" must be specified as a non-empty STRING with only alphanumeric and underscore characters!
  - "Columns" must be a non-empty LIST.
  - Field names must be non-empty STRINGS with only alphanumeric or underscore characters.
  - Field names cannot be "v[number]", "id", "confidence", "since" or "source" which are reserved Zillabyte names.
  - Field types may be "string", "integer", "float", "double", "boolean", "array" or "map"."""
  
  print_check_component_sink = """\n
"Outputs" Syntax:
  stream.outputs( name = "output_stream_name",
                  columns = [{"field_1" : "type_1"}, {"field_2" : "type_2"}, ...] )
  - "Outputs" stream "name" must be specified as a non-empty STRING with only alphanumeric and underscore characters!
  - "Columns" must be a non-empty LIST.
  - Field names must be non-empty STRINGS with only alphanumeric or underscore characters.
  - Field names cannot be "v[number]", "id", "confidence", "since" or "source" which are reserved Zillabyte names.
  - Field types may be "string", "integer", "float", "double", "boolean", "array" or "map"."""

  print_check_component_source = """\n
"Inputs" Syntax:
  component.inputs( name = "input_stream_name",
                    fields = [{"field_1" : "type_1"}, {"field_2" : "type_2"}, ...] )
  - "Inputs" stream "name" must be specified as a non-empty STRING with only alphanumeric and underscore characters!
  - "Fields" must be a non-empty LIST.
  - Field names must be non-empty STRINGS with only alphanumeric or underscore characters.
  - Field names cannot be "v[number]", "id", "confidence", "since" or "source" which are reserved Zillabyte names.
  - Field types may be "string", "integer", "float", "double", "boolean", "array" or "map"."""
  
  print_check_component_sink = """\n
"Outputs" Syntax:
  component_stream.outputs( name = "output_stream_name",
                            fields = [{"field_1" : "type_1"}, {"field_2" : "type_2"}, ...] )
  - "Outputs" stream "name" must be specified as a non-empty STRING with only alphanumeric and underscore characters!
  - "Fields" must be a non-empty LIST.
  - Field names must be non-empty STRINGS with only alphanumeric or underscore characters.
  - Field names cannot be "v[number]", "id", "confidence", "since" or "source" which are reserved Zillabyte names.
  - Field types may be "string", "integer", "float", "double", "boolean", "array" or "map"."""

  print_check_call_component = """\n
"Call_component" Syntax:
  stream.call_component( name = "name", \t\t\t\t\t\t\t\t\t => optional
                         component_id = "component_id_or_name",
                         additional_inputs = [other_input_stream_object_1, other_input_stream_object_2, ...], \t => blank if none
                         outputs = ["output_stream_name_1", "output_stream_name_2", ...], \t\t => optional for single output stream
                         output_format = "replace" OR "merge" ) \t => optional, defaults to "replace"
  - The "component_id" MUST be given and correspond to the id listed in the output of "zillabyte components".
  - The allowed output formats are "replace" and "merge". Note that only linear components, i.e. those with only "each" and "filter" operations support "merge".
      * "replace" - discards the input tuple values and only emits the output values. This is the default.
      * "merge" - re-emits the input tuple values along with the output values.
  - To correctly stich in the component, the implicit assumptions below WILL BE USED:
      * The "stream" that "call_component" is invoked on MUST correspond to the first listed input stream to the component.
      * The streams specified in "additional_inputs" MUST correspond to the other listed input streams in order.
      * Tuples emitted from the preceeding operation MUST contain the fields listed for the corresponding component input streams.
      * The streams specified in "outputs" must correspond to the listed output streams to the component in order.
      * The number of input and output streams specified must match the number listed for the component."""

  print_check_loop_back = """\n
"Loop_back" Syntax:
  stream.loop_back( operation_name[str], max_iterations[int] )"""
