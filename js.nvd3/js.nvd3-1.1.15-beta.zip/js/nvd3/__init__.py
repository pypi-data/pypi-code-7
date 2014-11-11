from fanstatic import Library, Resource, Group
import js.d3

library = Library('nvd3', 'resources')

nvd3 = Group([
    Resource(library, 'nv.d3.js', minified='nv.d3.min.js', depends=[js.d3.d3]),
    Resource(library, 'nv.d3.css', minified='nv.d3.min.css')])
