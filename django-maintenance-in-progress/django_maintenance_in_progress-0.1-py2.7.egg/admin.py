from django.contrib import admin

from maintenance_in_progress.models import Preferences


class PreferencesAdmin(admin.ModelAdmin):
    dummy = Preferences()
    pass


admin.site.register(Preferences, PreferencesAdmin)
