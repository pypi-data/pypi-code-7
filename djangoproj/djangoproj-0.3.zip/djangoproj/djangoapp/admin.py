from django.contrib import admin
from djangoapp.models import DjangoApp
# Register your models here.
class AdminDjangoApp(admin.ModelAdmin):
	prepopulated_fields = {'slug' : ('buttonName', )}
	#list_display = ('buttonName')
admin.site.register(DjangoApp, AdminDjangoApp)