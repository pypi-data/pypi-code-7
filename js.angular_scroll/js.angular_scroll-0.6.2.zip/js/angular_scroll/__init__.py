from fanstatic import Library, Resource
import js.angular

library = Library('angular-scroll', 'resources')

angular_scroll = Resource(
    library, 'angular-scroll.js',
    minified='angular-scroll.min.js',
    depends=[js.angular.angular])
