"""Admins for the aps_purchasing app."""
from django.contrib import admin

from . import models


class AMLAdmin(admin.ModelAdmin):
    list_display = ('ipn', 'manufacturer')
    search_fields = ('ipn__code', 'manufacturer__code', 'manufacturer__name')


class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('iso_code', 'name', 'sign')
    search_fields = ('iso_code', 'name', 'sign')
    list_editable = ('name', 'sign')


class DistributorAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'questionnaire_form', 'supplier_form', 'min_order_value',
        'currency', 'payment_terms', 'is_approved', 'is_active',
    )

    search_fields = (
        'name', 'questionnaire_form', 'supplier_form', 'min_order_value',
        'currency__iso_code', 'payment_terms__code', 'is_approved',
        'is_active',
    )

    list_editable = ('is_approved', 'is_active')


class DPNAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'ipn', 'distributor', 'mpn')
    search_fields = (
        'code', 'name', 'ipn__code', 'distributor__name', 'mpn__code',
        'mpn__name'
    )


class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')
    list_editable = ('name', )


class MPNAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'name', 'manufacturer', 'pku',
        'unit')
    search_fields = (
        'code', 'name', 'manufacturer__code', 'manufacturer__name', 'pku',
    )
    list_filter = ('manufacturer__name', 'unit')


class PackagingUnitAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name', )


class PaymentTermAdmin(admin.ModelAdmin):
    list_display = ('code', 'description')
    search_fields = ('code', 'description')


class PriceAdmin(admin.ModelAdmin):
    list_display = ('quotation_item', 'moq', 'price', 'currency')
    search_fields = ('moq', 'price', 'currency__iso_code')
    list_filter = ('currency__iso_code', )


class QuotationItemInline(admin.TabularInline):
    model = models.QuotationItem


class QuotationAdmin(admin.ModelAdmin):
    list_display = (
        'distributor', 'ref_number', 'issuance_date', 'expiry_date',
        'is_completed'
    )
    inlines = [QuotationItemInline]


class QuotationItemAdmin(admin.ModelAdmin):
    list_display = ('quotation', 'manufacturer', 'ipns', 'mpn',
                    'min_lead_time', 'max_lead_time')
    search_fields = (
        'quotation__ref_number', 'mpn__code', 'mpn__name' 'min_lead_time',
        'max_lead_time', 'manufacturer__name'
    )

    def ipns(self, obj):
        return ', '.join([
            aml.ipn.code for aml in obj.mpn.manufacturer.aml_set.all()])


admin.site.register(models.AML, AMLAdmin)
admin.site.register(models.Currency, CurrencyAdmin)
admin.site.register(models.Distributor, DistributorAdmin)
admin.site.register(models.DPN, DPNAdmin)
admin.site.register(models.Manufacturer, ManufacturerAdmin)
admin.site.register(models.MPN, MPNAdmin)
admin.site.register(models.PackagingUnit, PackagingUnitAdmin)
admin.site.register(models.PaymentTerm, PaymentTermAdmin)
admin.site.register(models.Price, PriceAdmin)
admin.site.register(models.Quotation, QuotationAdmin)
admin.site.register(models.QuotationItem, QuotationItemAdmin)
