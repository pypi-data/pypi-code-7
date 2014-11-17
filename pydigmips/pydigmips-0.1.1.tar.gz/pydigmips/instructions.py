import re
import sys
import collections

from . import compatibility

class SHIFTS:
    OPCODE = 13
    R1 = 10
    R2 = 7
    R3 = 4

INSTRUCTIONS = {}
def register(cls):
    INSTRUCTIONS[cls.opcode] = cls
    return cls

_Register = collections.namedtuple('_Register', ['id'])
class Register(_Register):
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

_ComputedAddress = collections.namedtuple('_ComputedAddress',
    ['register', 'offset'])
class ComputedAddress(_ComputedAddress):
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

    _re = re.compile('\[\s*r(?P<register>[0-7])(\s*\+\s*(?P<offset>[0-9]+))\s*\]')
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

_JumpAddress = collections.namedtuple('_JumpAddress', ['address'])
class JumpAddress(_JumpAddress):
    __slots__ = ()

    @classmethod
    def from_list(cls, l):
        return cls(l.pop(0),)

    @classmethod
    def from_string(cls, s):
        if not s.isdigit():
            raise ValueError('%s is not a valid jump address.' % s)
        return JumpAddress(int(s))

_Immediate = collections.namedtuple('_Immediate', ['value'])
class Immediate(_Immediate):
    __slots__ = ()

    @classmethod
    def from_list(cls, l):
        return cls(l.pop(0),)

    @classmethod
    def from_string(cls, s):
        if not s.isdigit():
            raise ValueError('%s is not a valid immediate.' % s)
        return Immediate(int(s))

def twos_comp(val, bits):
    """compute the 2's compliment of int value val"""
    if( (val&(1<<(bits-1))) != 0 ):
        val = val - (1<<bits)
    return val
class SignedImmediate(Immediate):
    @property
    def value(self):
        return twos_comp(super().value, 7)

class Instruction:
    __slots__ = ('arguments',)
    def __init__(self, *args):
        if not hasattr(self, '_spec') or not hasattr(self, '__call__') or \
                not hasattr(self, 'opcode'):
            raise NotImplementedError('%s is an abstract class.' %
                    self.__class__)
        if len(args) != len(self._spec):
            raise ValueError('%s expects %d arguments, not %d.' % (
                self.__class__.__name__.lower(),
                len(self._spec), len(args)))
        args = list(args)
        self.arguments = tuple(f.from_list(args) for f in self._spec)
        assert not args, args

    @classmethod
    def from_bytes(cls, b):
        cls = INSTRUCTIONS[b >> SHIFTS.OPCODE]
        b %= 2**SHIFTS.OPCODE
        return cls.from_bytes(b)

    def __getitem__(self, index):
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



class ArithmeticInstruction(Instruction):
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
    __slots__ = ()
    opcode = 0

    def __call__(self, state):
        state.registers[self[0].id] = state.registers[self[1].id] + \
            state.registers[self[2].id]

@register
class Sub(ArithmeticInstruction):
    __slots__ = ()
    opcode = 1

    def __call__(self, state):
        state.registers[self[0].id] = state.registers[self[1].id] + \
            state.registers[self[2].id]

class MemoryInstruction(Instruction):
    __slots__ = ()
    _spec = (Register, ComputedAddress)

    @classmethod
    def from_bytes(cls, b):
        (rdest, b) = divmod(b, 2**SHIFTS.R1)
        (rbase, offset) = divmod(b, 2**SHIFTS.R2)
        return cls(rdest, ComputedAddress(rbase, offset))


@register
class Ld(MemoryInstruction):
    __slots__ = ()
    opcode = 2

    def __call__(self, state):
        if self[1].offset == compatibility.MAGIC_IO_CONSTANT:
            char = sys.stdin.read(1)
            state.registers[self[0].id] = ord(char)
        else:
            addr = state.registers[self[1].register] + self[1].offset
            state.registers[self[0].id] = state.data[addr]

@register
class St(MemoryInstruction):
    __slots__ = ()
    opcode = 3

    def __call__(self, state):
        if self[1].offset == compatibility.MAGIC_IO_CONSTANT:
            char = state.registers[self[0].id]
            sys.stdout.write(chr(char))
        else:
            addr = state.register[self[1].register] + self[1].offset
            state.data[addr] = state.register[self[0]].id

@register
class Ble(Instruction):
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
    __slots__ = ()
    opcode = 7
    _spec = (JumpAddress,)

    @classmethod
    def from_bytes(cls, b):
        return cls(b)

    def __call__(self, state):
        state.pc = self[0].address
