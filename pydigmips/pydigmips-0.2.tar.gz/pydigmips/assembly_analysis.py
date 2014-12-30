"""Analyser of Assembly code that recognizes standard macros of the
compiler."""

import logging
import collections

from . import instructions

Push = collections.namedtuple('Push', ['arg', 'tmp'])
Pop = collections.namedtuple('Pop', ['arg', 'tmp'])

class Analyzer:
    def __init__(self, program):
        self.program = program

    def analyze(self):
        self.pops = self.recognize_pops()
        self.pushes = self.recognize_pushes()

    def get_stack_top(self, state):
        if state.registers[6] == 255:
            return None
        return state.data[state.registers[6]+1]

    def recognize_pushes(self):
        pushes = {}
        for (i, inst) in enumerate(self.program):
            try:
                (r, (six, offset)) = inst.match('st', None, None)
                if six != 6:
                    raise instructions.MatchError()
            except instructions.MatchError:
                continue
            pushes[i] = Push(r.id, None)
        return pushes

    def recognize_pops(self):
        pops = {}
        for (i, inst) in enumerate(self.program):
            try:
                (r, (six, offset)) = inst.match('ld', None, None)
                if six != 6:
                    raise instructions.MatchError()
            except instructions.MatchError:
                continue
            pops[i] = Pop(r.id, None)
        return pops



