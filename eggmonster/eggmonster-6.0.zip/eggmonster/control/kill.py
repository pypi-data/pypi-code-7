"""Send KILL signal to end forcibly."""
from eggmonster.control._common import control_command
import sys

def main():
    return control_command(sys.stdin, 'kill')
