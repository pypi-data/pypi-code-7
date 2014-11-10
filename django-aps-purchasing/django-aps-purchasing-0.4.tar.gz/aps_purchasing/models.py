"""Models of the aps_purchasing app."""
from django.db import models
from django.utils.translation import ugettext_lazy as _


class AML(models.Model):
    """
    Approved Manufacturer List.

    List of IPNs that may only be purchased through approved manufacturers.

    :ipn: The IPN instance.
    :manufacturer: A manufacturer who is approved for the given IPN.

    """
    ipn = models.ForeignKey(
        'aps_bom.IPN',
        verbose_name=_('Internal Part Number'),
    )

    manufacturer = models.ForeignKey(
        'aps_purchasing.Manufacturer',
        verbose_name=('Manufacturer'),
    )

    class Meta:
        verbose_name = _('AML')
        verbose_name_plural = _('AMLs')

    def __unicode__(self):
        return u'{0} - {1}'.format(self.ipn, self.manufacturer)


class Currency(models.Model):
    """
    Currency.

    :iso_code: The ISO code of this currency.
    :name: The name of this currency.
    :sign: The sign of this currency.

    """
    iso_code = models.CharField(
        verbose_name=_('ISO code'),
        max_length=3,
    )

    name = models.CharField(
        verbose_name=_('Name'),
        max_length=128,
    )

    sign = models.CharField(
        verbose_name=_('Sign'),
        max_length=1,
    )

    class Meta:
        verbose_name = _('Currency')
        verbose_name_plural = _('Currencies')

    def __unicode__(self):
        return self.iso_code


class Distributor(models.Model):
    """
    Distributor.

    :name: Name of this distributor.
    :questionnaire_form: Name of the form that was used for this distributor.
    :supplier_form: TODO: Describe this field.
    :min_order_value: Minimum order value for this distributor.
    :currency: Default currency for this distributor.
    :payment_terms: Payment terms for this distributor.
    :is_approved: If ``True``, this distributor is approved for business.
    :is_active: If ``False``, this distributor cannot be used, even if it was
      approved before.

    """
    name = models.CharField(
        verbose_name=_('Name'),
        max_length=128,
    )

    questionnaire_form = models.CharField(
        verbose_name=_('Questionnaire form'),
        max_length=128,
    )

    supplier_form = models.CharField(
        verbose_name=_('Supplier form'),
        max_length=128,
    )

    min_order_value = models.DecimalField(
        verbose_name=_('Minimum order value'),
        max_digits=11,
        decimal_places=5,
    )

    currency = models.ForeignKey(
        'aps_purchasing.Currency',
        verbose_name=_('Currency'),
    )

    payment_terms = models.ForeignKey(
        'aps_purchasing.PaymentTerm',
        verbose_name=_('Payment terms'),
        related_name='distributors',
    )

    is_approved = models.BooleanField(
        verbose_name=_('Is approved'),
        default=False,
    )

    is_active = models.BooleanField(
        verbose_name=_('Is active'),
        default=True,
    )

    def __unicode__(self):
        return self.name


class DPN(models.Model):
    """
    Distributor Part Number.

    :code: The code of this DPN.
    :ipn: The internal part number this DPN is mapped to.
    :distributor: The distributor who sells this part.
    :name: The name of this part.
    :mpn: The manufacturer part number for this part.

    """
    code = models.CharField(
        verbose_name=_('Code'),
        max_length=50,
    )

    ipn = models.ForeignKey(
        'aps_bom.IPN',
        verbose_name=_('Internal Part Number'),
        related_name='dpns',
        null=True, blank=True,
    )

    distributor = models.ForeignKey(
        'aps_purchasing.Distributor',
        verbose_name=_('Distributor'),
        related_name='dpns',
    )

    name = models.CharField(
        verbose_name=_('Name'),
        max_length=128,
    )

    mpn = models.ForeignKey(
        'aps_purchasing.MPN',
        verbose_name=_('Manufacturer Part Number'),
        related_name='dpns',
    )

    class Meta:
        verbose_name = _('DPN')
        verbose_name_plural = _('DPNs')

    def __unicode__(self):
        return self.code


class Manufacturer(models.Model):
    """
    Manufacturer.

    :code: Internal code for this manufacturer.
    :name: Name of this manufacturer.

    """
    code = models.CharField(
        verbose_name=_('Code'),
        max_length=50,
    )

    name = models.CharField(
        verbose_name=_('Name'),
        max_length=128,
    )

    def __unicode__(self):
        return self.name


class MPN(models.Model):
    """
    Manufacturer Part Number.

    :code: The code of this MPN.
    :manufacturer: The manufacturer of this part.
    :name: The name of this part.
    :pku: The amount of parts in one pacakge unit.
    :unit: The package unit of this part.

    """
    code = models.CharField(
        verbose_name=_('Code'),
        max_length=50,
    )

    manufacturer = models.ForeignKey(
        'aps_purchasing.Manufacturer',
        verbose_name=_('Manufacturer'),
    )

    name = models.CharField(
        verbose_name=_('Name'),
        max_length=128,
    )

    pku = models.FloatField(
        verbose_name=_('Amount per packaging unit'),
    )

    unit = models.ForeignKey(
        'aps_purchasing.PackagingUnit',
        verbose_name=_('PackagingUnit'),
    )

    class Meta:
        verbose_name = _('MPN')
        verbose_name_plural = _('MPNs')

    def __unicode__(self):
        return self.code


class PackagingUnit(models.Model):
    """
    Packaging Unit.

    :name: The name of this unit.

    """
    name = models.CharField(
        verbose_name=_('Name'),
        max_length=128,
    )

    def __unicode__(self):
        return self.name


class PaymentTerm(models.Model):
    """
    Payment term.

    :code: Internal code for this payment term.
    :description: Description of this payment term.

    """
    code = models.CharField(
        verbose_name=_('Code'),
        max_length=50,
    )

    description = models.CharField(
        verbose_name=_('Description'),
        max_length=128,
    )

    def __unicode__(self):
        return self.code


class Price(models.Model):
    """
    Price.

    :quotation_item: The quotation item this price belongs to.
    :moq: TODO: Describe this field
    :price: The price.
    :currency: The currency for this price.

    """
    quotation_item = models.ForeignKey(
        'aps_purchasing.QuotationItem',
        verbose_name=_('Quotation item'),
        related_name='prices',
    )

    moq = models.DecimalField(
        verbose_name=_('MOQ'),
        max_digits=11,
        decimal_places=5,
    )

    price = models.DecimalField(
        verbose_name=_('price'),
        max_digits=11,
        decimal_places=5,
    )

    currency = models.ForeignKey(
        Currency,
        verbose_name=_('Currency'),
        related_name='prices',
    )

    class Meta:
        ordering = ('price', )

    def __unicode__(self):
        return u'{0}: {1} {2}'.format(
            self.quotation_item, self.price, self.currency)

    def get_ipn(self):
        distributor = self.quotation_item.quotation.distributor
        qs = Price.objects.filter(
            quotation_item__mpn__DPNs__distributor=distributor)
        qs = qs.values_list(
            'quotation_item__mpn__DPNs__ipn__code').distinct()[0][0]
        return qs


class Quotation(models.Model):
    """
    Quotation.

    :distributor: The distributor offering this quotation.
    :ref_number: Reference number for this quotation.
    :issuance_date: Issuance date of this quotation.
    :expiry_date: Expiry date for this quotation.
    :completed: TODO: Describe this field.

    """
    distributor = models.ForeignKey(
        Distributor,
        verbose_name=_('Distributor'),
        related_name='quotations',
    )

    ref_number = models.CharField(
        verbose_name=_('Reference number'),
        max_length=128
    )

    issuance_date = models.DateTimeField(
        verbose_name=_('Issuance date'),
    )

    expiry_date = models.DateTimeField(
        verbose_name=_('Expiry date'),
    )

    is_completed = models.BooleanField(
        verbose_name=_('Completed'),
    )

    def __unicode__(self):
        return self.ref_number


class QuotationItem(models.Model):
    """
    Quotation item.

    :quotation: The quotation this item belongs to.
    :manufacturer: The manufacturer mannufacturing this product.
    :mpn: The MPN this quotation belongs refers to.
    :min_lead_time: TODO: Describe this field.
    :max_lead_time: TODO: Describe this field.

    """
    quotation = models.ForeignKey(
        Quotation,
        verbose_name=_('Quotation'),
        related_name='quotation_items',
    )

    manufacturer = models.ForeignKey(
        Manufacturer,
        verbose_name=_('Manufacturer'),
        related_name='quotations',
        blank=True, null=True,
    )

    mpn = models.ForeignKey(
        MPN,
        verbose_name=_('Manufacturer Part Number'),
        related_name='quotation_items',
    )

    min_lead_time = models.PositiveIntegerField(
        verbose_name=_('Minimum lead time'),
    )

    max_lead_time = models.PositiveIntegerField(
        verbose_name=_('Maximum lead time'),
    )

    def __unicode__(self):
        return u'{0} - {1}'.format(self.quotation, self.mpn)
