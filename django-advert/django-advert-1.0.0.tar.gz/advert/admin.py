from django.contrib import admin

from django.utils.translation import ugettext_lazy as _

from advert.models import Advertiser, TextAdvertisement, BannerAdvertisement


class AdvertiserAdmin(admin.ModelAdmin):
    """ Admin for the Advertiser Model. """
    fields = ('user', 'company_name', 'website')
    list_display = ('company_name', 'user', 'website')
    search_fields = ('company_name', 'user')

admin.site.register(Advertiser, AdvertiserAdmin)


class AdvertisementAdminBase(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('advertiser', 'title', 'content', 'status',
                       ('publish_on', 'publish_until'))
        }),
        ('Meta', {
            'fields': ('created', 'updated')
        })
    )
    readio_fields = {"status": admin.HORIZONTAL}
    readonly_fields = ('created', 'updated')
    list_display = ('title', 'status', 'advertiser', 'created', 'updated')
    list_editable = ('status',)
    list_filter = ('status', 'advertiser')
    search_fields = ('title', 'advertiser', 'content')


class TextAdvertisementAdmin(AdvertisementAdminBase):
    """ Admin for the Text Advertisement. """
    pass

admin.site.register(TextAdvertisement, TextAdvertisementAdmin)


class BannerAdvertismentAdmin(AdvertisementAdminBase):
    """ Admin for the Banner Advertisement. """
    search_fields = ('title', 'advertiser')

admin.site.register(BannerAdvertisement, BannerAdvertismentAdmin)