"""Models for the aps_production app."""
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import timedelta
from django.utils.translation import ugettext_lazy as _


class Error(models.Model):
    """
    An actual error, that occurred

    :order_run: on which order run this error occurred
    :error_bin: which error bin this belongs to
    :quantity: how often this error occurred during the run
    :comment: additional notes

    """
    order_run = models.ForeignKey(
        'aps_production.OrderRun',
        verbose_name=_('order run'),
        related_name='errors',
    )

    error_bin = models.ForeignKey(
        'aps_production.ErrorBin',
        verbose_name=_('error bin'),
        related_name='errors',
    )

    quantity = models.PositiveIntegerField(
        verbose_name=_('quantity'),
    )

    comment = models.TextField(
        verbose_name=_('comment'),
        blank=True,
    )


class ErrorBin(models.Model):
    """
    Master data containing all possible errors

    :technology: the technology the error is related to
    :error_code: an identifier for this error
    :description: a further description about this error
    :picture: ???

    """
    technology = models.ForeignKey(
        'aps_bom.Technology',
        verbose_name=_('technology'),
        related_name='error_bins',
    )

    error_code = models.CharField(
        verbose_name=_('error code'),
        max_length=64,
    )

    description = models.TextField(
        verbose_name=_('description'),
        blank=True,
    )

    picture = models.ImageField(
        verbose_name=_('picture'),
        blank=True, null=True,
        upload_to='error_bin_pictures',
    )

    class Meta:
        ordering = ('error_code', )


@python_2_unicode_compatible
class Order(models.Model):
    """
    An order placed by a customer.

    :order_number: unique string identifier for this order
    :company: the company, that placed the order
    :date_created: the date, this order was created
    :customer_po_number: ???
    :customer_po_date: ???

    """
    order_number = models.CharField(
        verbose_name=_('order number'),
        max_length=64,
        unique=True,
    )

    company = models.ForeignKey(
        'aps_bom.Company',
        verbose_name=_('company'),
        related_name='orders',
    )

    date_created = models.DateTimeField(
        verbose_name=_('date created'),
        auto_now_add=True,
    )

    customer_po_number = models.CharField(
        verbose_name=_('customer po number'),
        max_length=30,
    )

    customer_po_date = models.DateTimeField(
        verbose_name=_('customer po date'),
    )

    def __str__(self):
        return self.order_number

    class Meta:
        ordering = ('order_number', )


class OrderLine(models.Model):
    """
    Represents one line of an ``Order``.

    :order: The order this line belongs to.
    :line_no: the line number as entered by the planner
    :product: the product, this line is about
    :quantity_ordered: how many of this product, the customer orders
    :date_requested: when the customer requested the product

    computed:
    :date_shipped: When *all* items are shipped
    :date_delivered: The date of the last shipment plus the days it needs to
      ship to the customer

    """
    order = models.ForeignKey(
        Order,
        verbose_name=_('order'),
        related_name='order_lines',
    )

    line_no = models.CharField(
        verbose_name=_('line no'),
        max_length=4,
    )

    product = models.ForeignKey(
        'aps_bom.Product',
        verbose_name=_('product'),
        related_name='order_lines',
    )

    quantity_ordered = models.PositiveIntegerField(
        verbose_name=_('quantity ordered'),
    )

    date_requested = models.DateTimeField(
        verbose_name=_('date requested'),
    )

    @property
    def date_shipped(self):

        shipments = Shipment.objects.filter(
            order_run__in=self.order_runs.all(),
            # order_run__is_open=False,
        )
        if not shipments or shipments.filter(order_run__is_open=True).exists():
            return None
        # if the sum of all shipped items for this line is equal to all
        # actually produced items, we can consider it fully shipped
        if shipments.aggregate(models.Sum('quantity'))['quantity__sum'] == (
            self.order_runs.all().aggregate(models.Sum('quantity_out'))[
                'quantity_out__sum'
            ]
        ):
            return shipments.order_by('-date_shipped')[0].date_shipped
        return None

    @property
    def date_delivered(self):
        shipped = self.date_shipped
        shipping_days = self.order.company.shipping_days
        if not shipped or not shipping_days:
            return None
        return self.date_shipped + timedelta(
            days=self.order.company.shipping_days)

    class Meta:
        ordering = ('order', 'line_no')
        unique_together = ('order', 'line_no')


class OrderRun(models.Model):
    """
    One production run for a line of an order.

    :order_line: the order line, for which this run is run
    :run_number: the identifying number of this run
    :parent: reference to another order run
    :ipn: what IPN this goes under
    :quantity_started: what number of items we start the run with
    :quantity_dest_test: how many items have been destroyed in tests
    :quantity_out: how many items this run yielded. This plus the items
      destroyed in tests subtracted from the quantity we started with, equals
      the amount of items lost through errors.
    :is_open: if the run is still in progress. Defaults to True
    :comment: comments on this run for additional notes

    """
    order_line = models.ForeignKey(
        OrderLine,
        verbose_name=_('order line'),
        related_name='order_runs',
    )

    run_number = models.CharField(
        verbose_name=_('run number'),
        max_length=64,
    )

    parent = models.ForeignKey(
        'self',
        verbose_name=_('parent'),
        related_name='order_runs',
        blank=True, null=True,
    )

    ipn = models.ForeignKey(
        'aps_bom.IPN',
        verbose_name=_('ipn'),
        related_name='order_runs',
    )

    quantity_started = models.PositiveIntegerField(
        verbose_name=_('quantity started'),
    )

    quantity_dest_out = models.PositiveIntegerField(
        verbose_name=_('quantity dest out'),
        blank=True, null=True,
    )

    quantity_out = models.PositiveIntegerField(
        verbose_name=_('quantity out'),
        blank=True, null=True,
    )

    is_open = models.BooleanField(
        verbose_name=_('Is open'),
        default=True,
    )

    comment = models.TextField(
        verbose_name=_('comment'),
        blank=True,
    )


class Shipment(models.Model):
    """
    Stores data about when an order run is shipped

    :order_run: the ``OrderRun`` this shipment belongs to
    :quantity: how many items were shipped
    :date_shipped: when it was shipped

    """
    order_run = models.ForeignKey(
        OrderRun,
        verbose_name=_('order run'),
        related_name='shipments',
    )

    quantity = models.PositiveIntegerField(
        verbose_name=_('quantity'),
    )

    date_shipped = models.DateTimeField(
        verbose_name=_('date shipped'),
    )
