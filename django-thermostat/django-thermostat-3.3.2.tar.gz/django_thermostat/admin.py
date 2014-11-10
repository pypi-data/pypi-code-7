from django.contrib import admin
from models import *

class ThermometerAdmin(admin.ModelAdmin):
    pass
admin.site.register(Thermometer, ThermometerAdmin)

class RuleAdmin(admin.ModelAdmin):
    pass
admin.site.register(Rule, RuleAdmin)

class ConditionalAdmin(admin.ModelAdmin):
    pass
admin.site.register(Conditional, ConditionalAdmin)

class DayAdmin(admin.ModelAdmin):
    pass
admin.site.register(Day, DayAdmin)


class TimeRangeAdmin(admin.ModelAdmin):
    pass
admin.site.register(TimeRange, TimeRangeAdmin)

class ThermometerDataAdmin(admin.ModelAdmin):
    pass
admin.site.register(ThermometerData, ThermometerDataAdmin)

