# -*- coding: utf-8 -*-

__author__ = "Nikolay Dolganov"
__email__ = "SirNikolasd@yandex.ru"

# *********************************
# Page Titles
# *********************************

from cms.extensions.toolbar import ExtensionToolbar
from cms.toolbar_pool import toolbar_pool
from django.utils.translation import ugettext_lazy as _
from .models import Metadata


@toolbar_pool.register
class TitlesAndMetaExtensionToolbar(ExtensionToolbar):
    """
    Toolbar for the Title and META Fields
    """
    model = Metadata

    def populate(self):
        #current_page_menu = self._setup_extension_toolbar()
        current_page_menu = self.toolbar.get_or_create_menu('page')
        page_extension, url = self.get_page_extension_admin()
        current_page_menu.add_modal_item(_('Titles and META'), url=url,
                                                 disabled=not self.toolbar.edit_mode)