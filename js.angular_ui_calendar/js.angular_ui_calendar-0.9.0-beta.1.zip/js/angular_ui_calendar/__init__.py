from fanstatic import Library, Resource
import js.angular
import js.fullcalendar

library = Library('angular-ui-calendar', 'resources')

angular_ui_calendar = Resource(
    library,
    'calendar.js',
    depends=[js.angular.angular, js.fullcalendar.fullcalendar])
