from .state import State
from .instructions import Instruction

def load_hexa(stream):
    """Loads DigMIPS code from CAlias's assembler output on stdout."""
    return [Instruction.from_bytes(int(line, 16)) for line in stream]
