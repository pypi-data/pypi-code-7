# -*- coding: utf-8 -*-
"""
The main method to install the console script
"""
from argh import ArghParser

from optimus import __version__
from optimus.cli.build import build
from optimus.cli.watch import watch
from optimus.cli.init import init
from optimus.cli.po import po

def main():
    parser = ArghParser()
    parser.add_argument('-v', '--version', action='version', version=__version__)
    enabled_commands = [init, build, watch, po]
    
    # Enabling runserver command if cherrypy is installed
    try:
        import cherrypy
    except ImportError:
        pass
    else:
        from optimus.cli.runserver import runserver
        enabled_commands.append(runserver)
    
    parser.add_commands(enabled_commands)
    parser.dispatch()
