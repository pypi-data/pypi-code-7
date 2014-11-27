from django import forms
from django.conf import settings
from django.db import models
from django.contrib import admin
from django.contrib.staticfiles.templatetags.staticfiles import static

from reversion import VersionAdmin
from sorl.thumbnail import get_thumbnail

from .forms import AtLeastOneRequiredInlineFormSet
from .models import (
    ContentTranslation, BaseArticleTranslation, Article, Page,
    Category, CategoryTranslation, MediaItem, MediaCollection,
)


class CKModelAdminMixin(object):
    formfield_overrides = {models.TextField: {'widget': forms.Textarea(attrs={'class': 'ckeditor'})}, }

    class Media:
        js = [
            static('content/ckeditor/ckeditor.js'),
            static('content/ckeditor_setup.js'),
        ]

        css = {
            'all': (static('content/ckeditor_style_override.css'),)
        }


class CKMediaItemAdmin(admin.ModelAdmin, CKModelAdminMixin):
    list_display = ('thumbnail', 'file', 'title')
    prepopulated_fields = {'slug': ('file',), }

    @staticmethod
    def title(obj):
        return obj.translation.title

    def thumbnail(self, obj):
        if self.list_display_links is not None:
            return u'<img src="%s" />' % get_thumbnail(obj.file, '125x125', crop='center').url
        else:
            return u'<a href="%s" class="cklink"><img src="%s" /></a>' % (obj.file.url, get_thumbnail(obj.file, '125x125', crop='center').url)

    thumbnail.short_description = 'Thumb'
    thumbnail.allow_tags = True

    def changelist_view(self, request, extra_context=None, **kwargs):
        request.GET._mutable = True

        if 'CKEditor' in request.GET:
            request.GET.pop('CKEditor')
            request.GET.pop('langCode')
            asd = request.GET.pop('CKEditorFuncNum')
            request.session['CKEditorFuncNum'] = asd[0]
            request.session['asd'] = "klplkdglaskglaskdgl"
            request.session.save()
            self.list_display_links = None
        else:
            self.list_display_links = self._list_display_links_copy

        request.GET_mutable = False

        return super().changelist_view(request, extra_context=extra_context)

    def __init__(self, *args, **kwargs):
        self._list_display_links_copy = self.list_display_links
        super().__init__(*args, **kwargs)


class TranslationInline(admin.StackedInline):
    formset = AtLeastOneRequiredInlineFormSet
    max = len(settings.LANGUAGES)
    extra = 0


class BaseArticleTranslationInline(TranslationInline, CKModelAdminMixin):
    model = BaseArticleTranslation
    formset = AtLeastOneRequiredInlineFormSet
    max = len(settings.LANGUAGES)
    extra = 0


class BaseArticleAdmin(VersionAdmin, CKModelAdminMixin):
    inlines = (BaseArticleTranslationInline, )


class ContentTranslationInline(admin.StackedInline, CKModelAdminMixin):
    model = ContentTranslation
    max = len(settings.LANGUAGES)
    extra = 0


class MediaItemAdmin(CKMediaItemAdmin):
    inlines = (ContentTranslationInline, )


class CategoryTranslationInline(admin.StackedInline):
    model = CategoryTranslation
    max = len(settings.LANGUAGES)
    extra = 1


class CategoryAdmin(admin.ModelAdmin):
    inlines = (CategoryTranslationInline, )


admin.site.register(Category, CategoryAdmin)
admin.site.register(Article, BaseArticleAdmin)

admin.site.register(MediaItem, MediaItemAdmin)
admin.site.register(MediaCollection)

'''
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin


class ContentChildAdmin(PolymorphicChildModelAdmin, CKModelAdminMixin):
    base_model = Content


class ChildBaseArticleAdmin(BaseArticleAdmin, ContentChildAdmin):
    pass


class ContentAdmin(PolymorphicParentModelAdmin):
    base_model = Content
    child_models = (
        (Article, ContentChildAdmin),
        (Page, ContentChildAdmin),
    )

admin.site.register(Content, ContentAdmin)
'''
