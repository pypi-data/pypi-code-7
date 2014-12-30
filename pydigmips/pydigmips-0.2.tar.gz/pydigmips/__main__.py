import sys
import argparse

from . import loaders
from . import emulator
from . import compatibility

def main(fd, **kwargs):
    """Main function called from the command-line."""
    program = loaders.load_hexa(fd.readlines())
    e = emulator.Emulator(program, **kwargs)
    try:
        e.run_all()
    except emulator.SelfLoop:
        print()
        print('Self-loop detected. (“stop: j stop”?)')
    except emulator.InfiniteLoop:
        print()
        print('Infinite loop detected (same configuration twice).')
    except emulator.JumpZero:
        print()
        print('Jump to address 0 forbidden.')

parser = argparse.ArgumentParser(description='DigMIPS emulator.')
parser.add_argument('hexfile',
        type=argparse.FileType('r'),
        help='The STDOUT output of the assembler')
parser.add_argument('--infinite-loop', dest='infinite_loop',
        action='store_true',
        help='Enable simple infinite loop detection (stops when '
             'the emulator has been in the same state twice.)')
parser.add_argument('--jump-zero', dest='jump_zero',
        action='store_true',
        help='Stops the program when jumping to address 0 (probably '
             'an error caused by a non-initialized register).')
parser.add_argument('--beq', dest='beq',
        action='store_true',
        help='Use old instruction set, which implements BEQ instead of '
             'BLE at opcode 4.')
parser.add_argument('--old-magic-io', dest='old_magic_io',
        action='store_true',
        help='Use old magic constant for making I/O (255 instead of 63).')
parser.add_argument('--trace-inst', dest='trace_inst',
        action='store_true',
        help='Shows the Program Counter and the executed instruction '
             'while running.')
parser.add_argument('--trace-mem', dest='trace_mem',
        action='store_true',
        help='Show the state of registers and data memory while running.')
parser.add_argument('--trace-stack', dest='trace_stack',
        action='store_true',
        help='Displays translated function calls and stack, if the code '
             'uses the standard way of handling it.')
if __name__ == '__main__':
    args = parser.parse_args()
    compatibility.beq = args.beq
    if args.old_magic_io:
        compatibility.MAGIC_IO_CONSTANT = 255
    main(args.hexfile, infinite_loop=args.infinite_loop,
            trace_inst=args.trace_inst, trace_mem=args.trace_mem,
            trace_stack=args.trace_stack, jump_zero=args.jump_zero)
