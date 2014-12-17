# -*- coding: utf-8 -*-

__author__ = "Nikolay Dolganov"
__email__ = "SirNikolasd@yandex.ru"

from django.db import models
from cms.extensions import TitleExtension
from cms.extensions.extension_pool import extension_pool
from django.utils.translation import ugettext_lazy as _


# *********************************
# Page Titles
# *********************************


class Metadata(TitleExtension):
    """
    Custom titles and META fields for the page
    """

    ROBOTS_CHOICES = (
        ('index, follow', 'Index, Follow'),
        ('index, nofollow', 'Index, No Follow'),
        ('noindex, follow', 'No Index, Follow'),
        ('noindex, nofollow', 'No Index, No Follow'),
    )

    h1 = models.CharField(verbose_name=_('H1'), max_length=255, blank=True, null=True)
    keywords = models.TextField(verbose_name=_('Meta: Keywords'), blank=True, null=True)
    copyright = models.CharField(verbose_name=_('Meta: Copyright'), blank=True, null=True, max_length=255)
    author = models.CharField(verbose_name=_('Meta: Author'), blank=True, null=True, max_length=255)
    meta_robots = models.CharField(verbose_name=_('Meta: Robots'), choices=ROBOTS_CHOICES, default='index,follow',
                                   max_length=17)

    @property
    def meta_robots_value(self):
        """
        Returns Verbose Value of the meta_robots field
        :return: str
        """
        return dict(self.ROBOTS_CHOICES)[self.meta_robots]


extension_pool.register(Metadata)