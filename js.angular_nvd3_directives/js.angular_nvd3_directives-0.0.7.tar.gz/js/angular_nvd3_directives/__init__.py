from fanstatic import Library, Resource
import js.nvd3
import js.angular

library = Library('angularjs-nvd3-directives', 'resources')

angular_nvd3 = Resource(
    library,
    'angularjs-nvd3-directives.js',
    minified='angularjs-nvd3-directives.min.js',
    depends=[js.nvd3.nvd3, js.angular.angular])
