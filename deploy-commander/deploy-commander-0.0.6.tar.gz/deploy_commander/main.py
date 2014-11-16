import sys
import os
from fabric.main import main as fab_main

def main():
    fab_main(fabfile_locations=[os.path.join(os.path.dirname(__file__), 'fabfile')])