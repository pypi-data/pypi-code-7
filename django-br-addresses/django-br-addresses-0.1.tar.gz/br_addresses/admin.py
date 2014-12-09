# -*- coding:utf-8 -*-

# Stdlib imports


# Core Django imports
from django.contrib import admin

# Third-party app imports

# Realative imports of the 'app-name' package

from .models import City, Address
from .forms import CityForm, AddressForm


class CityAdmin(admin.ModelAdmin):

    form = CityForm

    list_display = (
        'state',
        'name',
        'created'
    )

    fieldsets = (
        (
            None,
            {
                'fields': (
                    'state',
                    'name',
                )
            }
        ),
    )

    date_hierarchy = 'created'

    search_fields = ('name', 'created', )

    list_filter = ('created', )

    list_per_page = 40


class AddressAdmin(admin.ModelAdmin):

    form = AddressForm

    list_display = (
        'city',
        'zip_code',
        'neighborhood',
        'street',
        'number',
        'complement',
        'created'
    )

    fieldsets = (
        (
            None,
            {
                'fields': (
                    'city',
                    'zip_code',
                    'neighborhood',
                    'street',
                    'number',
                    'complement',
                )
            }
        ),
    )

    date_hierarchy = 'created'

    search_fields = ('street', 'created', )

    list_filter = ('created', )

    list_per_page = 40


admin.site.register(City, CityAdmin)
admin.site.register(Address, AddressAdmin)
