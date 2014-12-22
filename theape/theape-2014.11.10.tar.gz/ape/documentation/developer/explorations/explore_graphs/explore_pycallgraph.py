
# third-party
from pycallgraph import PyCallGraph
from pycallgraph import GlobbingFilter
from pycallgraph import Config
from pycallgraph.output import GraphvizOutput

# this package
from ape.interface.ubootkommandant import UbootKommandant


subcommand = UbootKommandant()
graphviz = GraphvizOutput()
graphviz.output_file = 'figures/callgraphtest.png'
with PyCallGraph(output=graphviz):
   subcommand.list_plugins(None)


config = Config()
config.trace_filter = GlobbingFilter(exclude='*interface.arguments*'.split())
graphviz = GraphvizOutput()
graphviz.output_file = 'figures/filtered_graph.png'
with PyCallGraph(output=graphviz, config=config):
   subcommand.list_plugins(None)


DEPTH = 100
config = Config(max_depth=DEPTH)
graphviz = GraphvizOutput()
graphviz.output_file = 'figures/trimmed_graph.png'
with PyCallGraph(output=graphviz, config=config):
   subcommand.list_plugins(None)
