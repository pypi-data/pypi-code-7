"""Admin classes for the aps_production app."""
from django.contrib import admin

from . import models


# Inlines ====================================================================

class OrderLineInlineAdmin(admin.TabularInline):
    model = models.OrderLine


class OrderRunInlineAdmin(admin.TabularInline):
    model = models.OrderRun


class ShipmentInlineAdmin(admin.TabularInline):
    model = models.Shipment


# Admins =====================================================================

class ErrorAdmin(admin.ModelAdmin):
    """Custom admin for the ``Error`` model."""
    list_display = ('order_run', 'error_bin', 'quantity', 'comment')
    raw_id_fields = ['order_run', 'error_bin']


class ErrorBinAdmin(admin.ModelAdmin):
    """Custom admin for the ``ErrorBin`` model."""
    list_display = ('technology', 'error_code')
    search_fields = ['technology__identifier', 'error_code']


class OrderAdmin(admin.ModelAdmin):
    """Custom admin for the ``Order`` model."""
    list_display = ('order_number', 'company', 'date_created',
                    'customer_po_number', 'customer_po_date')
    search_fields = ['order_number']
    inlines = [OrderLineInlineAdmin]


class OrderLineAdmin(admin.ModelAdmin):
    """Custom admin for the ``OrderLine`` model."""
    list_display = ('order', 'line_no', 'product', 'quantity_ordered',
                    'date_requested', 'date_shipped', 'date_delivered')
    search_fields = ['order__order_number']
    raw_id_fields = ['order']
    inlines = [OrderRunInlineAdmin]


class OrderRunAdmin(admin.ModelAdmin):
    """Custom admin for the ```` model."""
    list_display = ('order_line', 'run_number', 'parent', 'ipn',
                    'quantity_started', 'quantity_dest_out', 'quantity_out',
                    'is_open', 'comment')
    list_filter = ['is_open']
    search_fields = ['run_number']
    raw_id_fields = ['order_line']
    inlines = [ShipmentInlineAdmin]


class ShipmentAdmin(admin.ModelAdmin):
    """Custom admin for the ``Shipment`` model."""
    list_display = ('order_run', 'quantity', 'date_shipped')
    raw_id_fields = ['order_run']


admin.site.register(models.Error, ErrorAdmin)
admin.site.register(models.ErrorBin, ErrorBinAdmin)
admin.site.register(models.Order, OrderAdmin)
admin.site.register(models.OrderLine, OrderLineAdmin)
admin.site.register(models.OrderRun, OrderRunAdmin)
admin.site.register(models.Shipment, ShipmentAdmin)
