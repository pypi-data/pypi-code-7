"""Instruction set of DigMIPS."""

import re
import sys
import collections

from . import compatibility

class SHIFTS:
    """Magic constants of the shifts to apply to extract arguments from
    hexadecimal code."""
    OPCODE = 13
    R1 = 10
    R2 = 7
    R3 = 4

class MatchError(Exception):
    pass

def twos_comp(val, bits):
    """compute the 2's compliment of int value val"""
    if( (val&(1<<(bits-1))) != 0 ):
        val = val - (1<<bits)
    return val

INSTRUCTIONS = {}
def register(cls):
    INSTRUCTIONS[cls.opcode] = cls
    return cls

_Register = collections.namedtuple('_Register', ['id'])
class Register(_Register):
    """Represents a register in an instruction."""
    __slots__ = ()

    @classmethod
    def from_list(cls, l):
        return cls(l.pop(0))

    @classmethod
    def from_string(cls, s):
        if len(s) != 2 or s[0] != 'r' or s[1] not in '01234567':
            raise ValueError('%s is not a valid register name' % s)
        return Register(int(s[1]))

    def __eq__(self, other):
        if not isinstance(other, Register):
            return False
        return self.id == other.id

    def __str__(self):
        return 'r%d' % self.id

_ComputedAddress = collections.namedtuple('_ComputedAddress',
    ['register', 'offset'])
class ComputedAddress(_ComputedAddress):
    """Represents an address computed from a register and an offset."""
    __slots__ = ()

    @classmethod
    def from_list(cls, l):
        item = l.pop(0)
        if isinstance(item, tuple):
            (register, offset) = item
        else:
            register = item
            offset = l.pop(0)
        return cls(register, offset)

    _re = re.compile(r'\[\s*r(?P<register>[0-7])(\s*\+\s*(?P<offset>[0-9]+))\s*\]')
    @classmethod
    def from_string(cls, s):
        matched = cls._re.match(s)
        if not matched:
            raise ValueError('%s is not a valid computer address.' % s)
        return cls(int(matched.group('register')),
                int(matched.group('offset') or '0'))

    def __eq__(self, other):
        if not isinstance(other, ComputedAddress):
            return False
        return self.register == other.register and \
                self.offset == other.offset

    def __str__(self):
        # TODO: negative offsets
        return '[%s + %d]' % (self.register, self.offset)

_JumpAddress = collections.namedtuple('_JumpAddress', ['address'])
class JumpAddress(_JumpAddress):
    """An address given as an immediate."""
    __slots__ = ()

    @classmethod
    def from_list(cls, l):
        return cls(l.pop(0),)

    @classmethod
    def from_string(cls, s):
        if not s.isdigit():
            raise ValueError('%s is not a valid jump address.' % s)
        return JumpAddress(int(s))

    def __str__(self):
        return str(self.address)

_Immediate = collections.namedtuple('_Immediate', ['value'])
class Immediate(_Immediate):
    """An immediate value."""
    __slots__ = ()

    @classmethod
    def from_list(cls, l):
        return cls(l.pop(0),)

    @classmethod
    def from_string(cls, s):
        if not s.isdigit():
            raise ValueError('%s is not a valid immediate.' % s)
        return Immediate(int(s))

    def __str__(self):
        return str(self.value)

class SignedImmediate(Immediate):
    """A signed immediate, used for offsets."""
    @property
    def value(self):
        return twos_comp(super().value, 7)

class Instruction:
    """Abstract class for instructions."""
    __slots__ = ('arguments',)
    def __init__(self, *args):
        self.check_not_abstract()
        self.check_args(args)
        args = list(args)
        self.arguments = tuple(f.from_list(args) for f in self._spec)
        assert not args, args

    def check_not_abstract(self):
        """Raises an exception if the class is abstract."""
        if not hasattr(self, '_spec') or not hasattr(self, '__call__') or \
                not hasattr(self, 'opcode'):
            raise NotImplementedError('%s is an abstract class.' %
                    self.__class__)

    def check_args(self, args):
        """Checks arguments given to the constructor with respect to
        the spec."""
        if len(args) != len(self._spec):
            raise ValueError('%s expects %d arguments, not %d.' % (
                self.__class__.__name__.lower(),
                len(self._spec), len(args)))

    def match(self, inst, *args):
        """Check equality with holes. Also returns the arguments."""
        # Match the instruction
        if inst.lower() != self.__class__.__name__.lower():
            raise MatchError()
        # Same instruction, so it should have the same number of args
        assert len(args) == len(self.arguments)
        # We give arguments to specifiers using the star syntax, so
        # they have to be tuples; but we also want to allow integers
        # and None for the sake of readability -> convert them.
        args = [x if isinstance(x, tuple) else (x,) for x in args]
        # Check they are either equal or there is a hole.
        if all(x == (None,) or f(*x) == y for (x, f, y) in
                zip(args, self._spec, self.arguments)):
            return self.arguments
        raise MatchError()

    @classmethod
    def from_bytes(cls, b):
        """Parses an instruction from a bytes stream."""
        cls = INSTRUCTIONS[b >> SHIFTS.OPCODE]
        b %= 2**SHIFTS.OPCODE
        return cls.from_bytes(b)

    def __getitem__(self, index):
        """Returns the i-th argument of the instruction."""
        return self.arguments[index]

    def __repr__(self):
        return '<pydigmips.instructions.%s(%s)>' % \
            (self.__class__.__name__,
             ', '.join(map(str, self.arguments)))

    def __eq__(self, other):
        if not isinstance(other, Instruction):
            return False
        return self.opcode == other.opcode and \
                self.arguments == other.arguments

    def __str__(self):
        """Returns a representation in assembly code."""
        args = ', '.join(map(str, self.arguments))
        return '%s %s' % (self.__class__.__name__.lower(), args)



class ArithmeticInstruction(Instruction):
    """Abstract class for ADD and SUB."""
    __slots__ = ()
    _spec = (Register, Register, Register)

    @classmethod
    def from_bytes(cls, b):
        (r1, b) = divmod(b, 2**SHIFTS.R1)
        (r2, b) = divmod(b, 2**SHIFTS.R2)
        (r3, b) = divmod(b, 2**SHIFTS.R3)
        assert b == 0, (r1, r2, r3, b)
        return cls(r1, r2, r3)


@register
class Add(ArithmeticInstruction):
    """ADD instruction."""
    __slots__ = ()
    opcode = 0

    def __call__(self, state):
        s = (state.registers[self[1].id] + state.registers[self[2].id])
        state.registers[self[0].id] = s % (2**8)

@register
class Sub(ArithmeticInstruction):
    """SUB instruction."""
    __slots__ = ()
    opcode = 1

    def __call__(self, state):
        s = (state.registers[self[1].id] - state.registers[self[2].id])
        if s < 0:
            s += 256
        state.registers[self[0].id] = s % (2**8)

class MemoryInstruction(Instruction):
    """Abstract class for ST and LD."""
    __slots__ = ()
    _spec = (Register, ComputedAddress)

    @classmethod
    def from_bytes(cls, b):
        (rdest, b) = divmod(b, 2**SHIFTS.R1)
        (rbase, offset) = divmod(b, 2**SHIFTS.R2)
        if offset > 63:
            offset -= 128
        return cls(rdest, ComputedAddress(rbase, offset))


@register
class Ld(MemoryInstruction):
    """LD instruction."""
    __slots__ = ()
    opcode = 2

    def __call__(self, state):
        if self[1].offset == compatibility.MAGIC_IO_CONSTANT:
            char = sys.stdin.read(1)
            state.registers[self[0].id] = ord(char)
        else:
            addr = state.registers[self[1].register] + self[1].offset
            addr = addr % (2**8)
            state.registers[self[0].id] = state.data[addr]

@register
class St(MemoryInstruction):
    """ST instruction."""
    __slots__ = ()
    opcode = 3

    def __call__(self, state):
        if self[1].offset == compatibility.MAGIC_IO_CONSTANT:
            char = state.registers[self[0].id]
            if char == 13: # \r
                char = 10
            sys.stdout.write(chr(char))
        else:
            addr = state.registers[self[1].register] + self[1].offset
            addr = addr % (2**8)
            state.data[addr] = state.registers[self[0].id]

@register
class Ble(Instruction):
    """BLE instruction."""
    __slots__ = ()
    opcode = 4
    _spec = (Register, Register, SignedImmediate)

    @classmethod
    def from_bytes(cls, b):
        (r1, b) = divmod(b, 2**SHIFTS.R1)
        (r2, addr) = divmod(b, 2**SHIFTS.R2)
        return cls(r1, r2, addr)

    if compatibility.BEQ_MODE:
        def __call__(self, state):
            if state.registers[self[0].id] == state.registers[self[1].id]:
                state.pc += self[2].value # += 1 done before call
    else:
        def __call__(self, state):
            if state.registers[self[0].id] <= state.registers[self[1].id]:
                state.pc += self[2].value # += 1 done before call

@register
class Ldi(Instruction):
    """LDI instruction."""
    __slots__ = ()
    opcode = 5
    _spec = (Register, Immediate) # TODO: handle chars

    @classmethod
    def from_bytes(cls, b):
        (rdest, imm) = divmod(b, 2**SHIFTS.R1)
        assert imm < 2**8
        return cls(rdest, imm)

    def __call__(self, state):
        state.registers[self[0].id] = self[1].value

@register
class Ja(Instruction):
    """JA instruction."""
    __slots__ = ()
    opcode = 6
    _spec = (Register, Register)

    @classmethod
    def from_bytes(cls, b):
        (r1, b) = divmod(b, 2**SHIFTS.R1)
        (r2, zero) = divmod(b, 2**SHIFTS.R2)
        assert zero == 0, zero
        assert r1 < 2**5, r1
        return cls(r1, r2)

    def __call__(self, state):
        high = state.registers[self[0].id]
        low = state.registers[self[1].id]
        state.pc = (high << 8) + low

@register
class J(Instruction):
    """J instruction."""
    __slots__ = ()
    opcode = 7
    _spec = (JumpAddress,)

    @classmethod
    def from_bytes(cls, b):
        return cls(b)

    def __call__(self, state):
        state.pc = self[0].address
