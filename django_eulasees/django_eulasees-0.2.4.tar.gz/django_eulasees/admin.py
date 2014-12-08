from django.contrib import admin

from django_eulasees import models

# admin site stuff
admin.site.register(models.Tag)
admin.site.register(models.SnippetTag)
admin.site.register(models.TagIcon)
admin.site.register(models.TagEula)

class EulaSnippetInline(admin.TabularInline):
    model = models.EulaSnippet

class SnippetTagInline(admin.TabularInline):
    model = models.SnippetTag

@admin.register(models.EulaSnippet)
class EulaSnippetAdmin(admin.ModelAdmin):
    inlines = (SnippetTagInline,)

@admin.register(models.RawEula)
class RawEulaAdmin(admin.ModelAdmin):
    inlines = (EulaSnippetInline,)


    
