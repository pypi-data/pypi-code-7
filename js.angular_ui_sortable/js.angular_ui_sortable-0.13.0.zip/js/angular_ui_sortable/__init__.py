from fanstatic import Library, Resource
import js.jquery
import js.jqueryui
import js.angular

library = Library('angular_ui_sortable', 'resources')

sortable = Resource(
    library, 'sortable.js',
    depends=[js.jquery.jquery, js.angular.angular, js.jqueryui.jqueryui])
