from django.contrib import admin

# Register your models here.
from image_cropping import ImageCroppingMixin
from .models import FotoramaSlider


class FotoramaSliderAdmin(ImageCroppingMixin, admin.ModelAdmin):
    list_display = ['admin_img', 'name', 'query', 'order', 'created']
    search_fields = ['name', 'query']
    list_filter = ['created', ]
    readonly_fields = ['created', 'modify']
    list_display_links = ['admin_img', 'name']

admin.site.register(FotoramaSlider, FotoramaSliderAdmin)