"""Forms for the ``aps_purchasing`` app."""
from csv import DictReader

from django import forms
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as __

from .models import (
    Currency,
    Manufacturer,
    MPN,
    PackagingUnit,
    Price,
    Quotation,
    QuotationItem,
)


class QuotationUploadForm(forms.ModelForm):
    """Upload form for quotation csv files to create or update Quotations."""

    quotation_file = forms.FileField()

    def append_error(self, error_message):
        if '__all__' in self.errors:
            if error_message not in self.errors['__all__']:
                self.errors['__all__'].append(error_message)
        else:
            self.errors['__all__'] = [error_message]

    def clean(self):
        cleaned_data = super(QuotationUploadForm, self).clean()

        # don't do anything with the file if there are errors already
        if any(self.errors):
            return cleaned_data

        try:
            model_kwargs = cleaned_data.copy()
            model_kwargs.pop('quotation_file')
            self.instance = Quotation.objects.get(**model_kwargs)
        except Quotation.DoesNotExist:
            pass

        # initiate the csv dictreader with the uploaded file
        csv_file = self.files.get('quotation_file')
        self.reader = DictReader(csv_file)

        # update the fieldnames to match the ones on the model
        new_names = []
        for fieldname in self.reader.fieldnames:
            new_names.append(fieldname.lower())
        self.reader.fieldnames = new_names

        # iterate over the lines and clean the values
        self.cleaned_quotation = []
        for line_dict in self.reader:
            quotation_itemdict = {}
            price_dict = {}
            # here we make use of the fact, that the manufacturer is always
            # parsed first, meaning, that if manufacturer still is None, when
            # we reach the mpn value, we know, that it hasn't been found
            # previously
            manufacturer = None
            line_list = [pair for pair in line_dict.iteritems()]
            # just to make sure, tha sequence of columns didn't change
            # if manufacturer would at some point occur before mpn, we wouldn't
            # need to reverse the order of keys
            if line_dict.keys().index('manufacturer') > line_dict.keys().index(
                    'mpn'):
                line_list.reverse()
            for key, value in line_list:
                if key == 'manufacturer':
                    try:
                        manufacturer = Manufacturer.objects.get(
                            name__iexact=value,
                        )
                    except Manufacturer.DoesNotExist:
                        this_link = (
                            '<a href="{0}" target="_blank">{0}</a>'.format(
                                reverse(
                                    'admin:aps_purchasing_manufacturer_add')))
                        self.append_error(__(
                            'The manufacturer "{0}" does not exist.'
                            ' Please create it first. {1}'.format(
                                value, this_link)))
                    else:
                        quotation_itemdict[key] = manufacturer
                if key == 'mpn' and manufacturer is not None:
                    pckg_unit = PackagingUnit.objects.get_or_create(
                        name=line_dict.get('unit'))[0]
                    try:
                        mpn = MPN.objects.get(
                            code=value,
                            manufacturer=manufacturer)
                    except MPN.DoesNotExist:
                        mpn = MPN.objects.create(
                            code=value, manufacturer=manufacturer,
                            unit=pckg_unit, name=line_dict.get('description'),
                            pku=line_dict.get('pku'))
                    quotation_itemdict[key] = mpn
                if key in ['moq', 'price']:
                    price_dict[key] = value
                if key == 'currency':
                    try:
                        currency = Currency.objects.get(iso_code=value)
                    except Currency.DoesNotExist:
                        this_link = (
                            '<a href="{0}" target="_blank">{0}</a>'.format(
                                reverse('admin:aps_purchasing_currency_add')))
                        self.append_error(__(
                            'The currency "{0}" does not exist.'
                            ' Please create it first. {1}'.format(
                                value, this_link)))
                    else:
                        price_dict[key] = currency
                if key == 'lead_time_min':
                    quotation_itemdict['min_lead_time'] = value
                if key == 'lead_time_max':
                    quotation_itemdict['max_lead_time'] = value
            quotation_itemdict['price'] = price_dict
            self.cleaned_quotation.append(quotation_itemdict)
        return cleaned_data

    def save(self):
        instance = super(QuotationUploadForm, self).save()
        for quotation_itemdict in self.cleaned_quotation:
            quotation_itemdict['quotation'] = instance
            price_dict = quotation_itemdict.pop('price')
            quotation_item = QuotationItem.objects.get_or_create(
                **quotation_itemdict)[0]
            price_dict['quotation_item'] = quotation_item
            Price.objects.get_or_create(**price_dict)
        return instance

    class Meta:
        model = Quotation
        fields = (
            'distributor', 'is_completed', 'ref_number', 'issuance_date',
            'expiry_date', 'quotation_file', )
