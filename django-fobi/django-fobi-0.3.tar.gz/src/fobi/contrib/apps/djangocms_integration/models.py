__title__ = 'fobi.contrib.apps.djangocms_integration.widgets'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = 'Copyright (c) 2014 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('FobiFormWidget',)

from django.db import models
from django.utils.translation import ugettext_lazy as _

from cms.models import CMSPlugin
from cms.utils.compat.dj import python_2_unicode_compatible


@python_2_unicode_compatible
class FobiFormWidget(CMSPlugin):
    """
    Plugin for storing ``django-fobi`` form reference.
    """
    form_entry = models.ForeignKey('fobi.FormEntry', verbose_name=_("Form"))

    def __str__(self):
        return self.form_entry.name

    search_fields = ('form_entry__name',)
