"""Tests for the forms of the ``aps_purchasing`` app."""
import os

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils.timezone import now

from ..forms import QuotationUploadForm
from ..models import MPN, Price, Quotation, QuotationItem
from .factories import (
    CurrencyFactory,
    DistributorFactory,
    ManufacturerFactory,
)


class QuotationUploadFormTestCase(TestCase):
    """Tests for the ``QuotationUpoadForm`` form class."""
    longMessage = True

    def setUp(self):
        self.distributor = DistributorFactory()

        self.quotation_file = open(os.path.join(
            settings.APP_ROOT, 'tests/files/Quotation.csv'))

        self.data = {
            'distributor': self.distributor.pk,
            'ref_number': 'REF123',
            'issuance_date': now(),
            'expiry_date': now(),
            'is_completed': True,
        }
        self.files = {
            'quotation_file': SimpleUploadedFile('Quotation.csv',
                                                 self.quotation_file.read()),
        }

    def test_form(self):
        form = QuotationUploadForm(data=self.data)
        self.assertFalse(form.is_valid(), msg='The form should not be valid.')

        form = QuotationUploadForm(data=self.data, files=self.files)
        self.assertFalse(form.is_valid(), msg=(
            'Without all the currencies in the DB, the form should not be'
            ' valid.'))
        self.usd = CurrencyFactory(iso_code='USD')

        form = QuotationUploadForm(data=self.data, files=self.files)
        self.assertFalse(form.is_valid(), msg=(
            'Without all the manufacturers in the DB, the form should not be'
            ' valid.'))
        ManufacturerFactory(name='Samsung')
        ManufacturerFactory(name='TDK')

        form = QuotationUploadForm(data=self.data, files=self.files)
        self.assertTrue(form.is_valid(), msg=(
            'The form should be valid. Errors: {0}'.format(form.errors)))

        form.save()
        self.assertEqual(Quotation.objects.count(), 1, msg=(
            'After form save, there should be one Quotation in the database.'))
        self.assertEqual(QuotationItem.objects.count(), 2, msg=(
            'After form save, there should be four QuotationItems in the'
            ' database.'))
        self.assertEqual(Price.objects.count(), 4, msg=(
            'Afte form save, there should be three Prices in the database.'))
        self.assertEqual(MPN.objects.count(), 2, msg=(
            'Afte form save, there should be four new MPNs in the database.'))
