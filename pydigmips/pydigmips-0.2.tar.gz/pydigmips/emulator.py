"""Contains the emulator itself."""

import time

from .state import State
from . import instructions
from .assembly_analysis import Analyzer

class Halt(Exception):
    pass
class InfiniteLoop(Exception):
    pass
class SelfLoop(Exception):
    """Raised when an instruction jumps to itself."""
class JumpZero(Exception):
    pass

def format_cell(x):
    """Formats the content of a cell so it is displayed nicely."""
    r = hex(x)[2:]
    if len(r) == 1:
        r = '0' + r
    return r.upper()

class Emulator:
    """Emulator of DigMIPS code."""
    def __init__(self, program, state=None, infinite_loop=False,
            trace_inst=False, trace_mem=False, trace_stack=False,
            jump_zero=False):
        self.trace_inst = trace_inst
        self.trace_mem = trace_mem
        self.trace_stack = trace_stack
        self.program = program
        self.state = state or State()
        self.previous_states = set()
        self.detect_same_config = infinite_loop
        self.forbid_jump_zero = jump_zero
        self.analyzer = Analyzer(program)
        self.analyzer.analyze()

    def show_trace(self):
        """If the options ask for it, displays the trace."""
        inst = self.program[self.state.pc]
        if self.trace_mem:
            print('Registers: %r' % self.state.registers)
            print('Data: %s' % ' '.join(map(format_cell, self.state.data)))
        if self.trace_inst:
            print('%.03d: %s' % (self.state.pc, inst))
        if self.trace_stack:
            if self.state.pc in self.analyzer.pushes:
                id = self.analyzer.pushes[self.state.pc].arg
                print('%.03d: Pushed %d (r%d)' % (self.state.pc,
                    self.state.registers[id], id))
            if self.state.pc in self.analyzer.pops:
                id = self.analyzer.pops[self.state.pc].arg
                print('%.03d: Poped %d (r%d)' % (self.state.pc,
                    self.analyzer.get_stack_top(self.state), id))


    def run_one(self):
        """Run one instruction."""
        if self.state.pc >= len(self.program):
            raise Halt()
        inst = self.program[self.state.pc]
        self.show_trace()
        old_pc = self.state.pc
        self.state.pc += 1
        inst(self.state)
        if self.forbid_jump_zero and self.state.pc == 0:
            raise JumpZero()
        """
        assert self.state.registers[7] == 0 or \
                self.state.registers[7] >= self.state.registers[6], \
                (self.state.registers, old_pc,
                        self.program[old_pc])"""
        self.detect_loops(old_pc)

    def detect_loops(self, old_pc):
        """Determines if we are in a self-loop (using the old_pc) and/or
        in an infinite loop (if the options ask for it)."""
        if self.state.pc == old_pc:
            raise SelfLoop()
        if self.detect_same_config:
            if self.state.freeze() in self.previous_states:
                raise InfiniteLoop()
            self.previous_states.add(self.state.freeze())

    def run(self, max_steps):
        """Run for a certain number of steps."""
        for x in range(0, max_steps):
            self.run_one()

    def run_all(self):
        """Run until we reach the end of the program."""
        try:
            while True:
                self.run_one()
        except Halt:
            pass
