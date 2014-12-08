from fanstatic import Library, Resource
import js.angular

library = Library('angular_infinitescroll', 'resources')

infinite_scroll = Resource(
    library, 'ng-infinite-scroll.js',
    minified='ng-infinite-scroll.min.js',
    depends=[js.angular.angular])
