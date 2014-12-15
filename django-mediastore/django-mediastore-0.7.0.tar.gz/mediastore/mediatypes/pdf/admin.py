from django import forms
from django.contrib import admin
from mediastore.admin import MediaAdmin
from mediastore.mediatypes.pdf.models import PDF


class PDFAdmin(MediaAdmin):
    list_display = ('id', 'name', 'file_size', 'created')


admin.site.register(PDF, PDFAdmin)
