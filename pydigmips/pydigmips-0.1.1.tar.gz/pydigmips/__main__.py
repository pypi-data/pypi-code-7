import sys

from . import loaders
from . import emulator

def main(filename):
    with open(filename) as fd:
        program = loaders.load_hexa(fd.readlines())
    e = emulator.Emulator(program)
    e.run_all()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Syntax: %s file.ram' % sys.argv[0])
        exit(1)
    main(sys.argv[1])
