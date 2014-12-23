from docutils import nodes
from dot_parser import parse_dot_data


def closed_dotgraphdirective(build):
    'Close the directive with the build directory'
    def DotgraphDirective(name, arguments, options, content, *args):
        graph = parse_dot_data('\n'.join(content))
        outpath = arguments[0]
        graph.write_svg(build + outpath)
        html = '<img src="{0}" class="dot-graph" />'.format(outpath)
        return [nodes.raw('', html, format='html')]
    DotgraphDirective.arguments = (1, 0, 1)
    DotgraphDirective.content = 1
    return DotgraphDirective
