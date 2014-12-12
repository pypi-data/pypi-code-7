from counter import Counter

class JvmOperation:
  def __init__(self, op_type):
    self._type = op_type

  def build_node(self, *args):
    self._name = self._type+"_"+Counter.get()
    self._emits = ["stream_"+Counter.get()]
    self._args = args

  def run_operation(self):
    print self._type+" operation can only be instantiated on our cluster, sorry!"
