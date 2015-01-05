from django.conf import settings

from django.db import models

from django.utils.translation import ugettext_lazy as _

from advert.managers import AdvertisementManager

STATUS_DRAFT = 0
STATUS_PUBLISHED = 1
STATUS = (
    (STATUS_DRAFT, 'Draft'),
    (STATUS_DRAFT, 'Published')
)


class AdvertiserBase(models.Model):
    """ Base class for the advertiser. """
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    company_name = models.CharField(_(u'Company Name'), max_length=150)
    website = models.URLField(verbose_name=_(u'Company Website'), blank=True, 
                              null=True)

    class Meta:
        verbose_name = _(u'Advertiser')
        verbose_name_plural = _(u'Advertisers')
        ordering = ('company_name',)
        abstract = True

    def __str__(self):
        return self.company_name


class Advertiser(AdvertiserBase):
    pass


class AdvertisementBase(models.Model):
    """ Base class for the advertisements. """
    advertiser = models.ForeignKey(Advertiser)
    title = models.CharField(_(u'Title'), max_length=150)

    status = models.IntegerField(default=STATUS_DRAFT, choices=STATUS)
    publish_on = models.DateTimeField(verbose_name=_(u'Publish On'), blank=True,
                                      null=True)
    publish_until = models.DateTimeField(verbose_name=_(u'Published Until'),
                                         blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects =  AdvertisementManager()

    class Meta:
        verbose_name = _(u'Advertisement')
        verbose_name_plural = _(u'Advertisements')
        ordering = ('title',)
        abstract = True

    def __str__(self):
        return self.title


class TextAdvertisement(AdvertisementBase):
    """ Used for Text only advertisements. """
    content = models.TextField()

    class Meta:
        verbose_name = _(u'Text Advertisement')
        verbose_name_plural = _(u'Text Advertisements')


class BannerAdvertisement(AdvertisementBase):
    """ Used for Banne advertisements. """
    content = models.ImageField(upload_to='advertisements/banner')

    class Meta:
        verbose_name = _(u'Banner Advertisement')
        verbose_name_plural = _(u'Banner Advertisements')

