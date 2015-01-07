#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

from io import open
import sys

class TextPIO(object):
    """Class for handling basic text input/output."""
    
    def __init__(self, filepath):
        self.file = filepath
        self.re_eol = re.compile("\n?$")
        
    def load(self):
        lines = None
        try:
            with open(self.file, mode='r', encoding='utf-8') as handle:
                lines = handle.readlines()
                eol = handle.newlines
                lines = [ line.rstrip(eol) for line in lines ]
        except (IOError, OSError, ValueError) as e:
            raise e
        return lines
         
    def save(self, output):
        try:
            with open(self.file, mode='w', encoding='utf-8') as handle:
                for line in output:
                    self.re_eol.sub("\n", line)
                    handle.write(line)
        except (IOError, OSError, ValueError) as e:
            raise e

class TextInput(object):
    """Iterator class for processing text input."""
    
    def __init__(self, handle):
        self.handle = handle
        
    def __next__(self):
        input = self.handle.next()
        record = input.rstrip()
        return record
        
    def __iter__(self):
        return iter(self.__next__, None)
        
    def next(self):
        return self.__next__()
            
class TextOutput(object):
    """Iterator class for processing text output."""
    
    def __init__(self, handle):
        self.handle = handle
        
    def write(self, line):
        self.re_eol.sub("\n", line)
        self.handle.write(line)
