from .models import Action, Right
from django.contrib import admin

class ActionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class RightAdmin(admin.ModelAdmin):
    list_display = ('id_group','id_resource','actions',)
    search_fields = ('id_group',)



admin.site.register(Action, ActionAdmin)
admin.site.register(Right, RightAdmin)
