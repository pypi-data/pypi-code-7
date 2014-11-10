"""Tests for the views of the ``aps_purchasing`` app."""
import os

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils.timezone import now

from django_libs.tests.mixins import ViewRequestFactoryTestMixin
from django_libs.tests.factories import UserFactory
from aps_bom.tests.factories import BOMFactory

from ..factories import (
    CurrencyFactory,
    DistributorFactory,
    ManufacturerFactory,
    PriceFactory,
)
from ...models import Quotation, QuotationItem, Price
from ... import views


class QuotationUploadViewTestCase(ViewRequestFactoryTestMixin, TestCase):
    """Tests for the ``QuotationUploadView`` view class."""
    longMessage = True
    view_class = views.QuotationUploadView

    def get_view_name(self):
        return 'aps_purchasing_quotation_upload'

    def setUp(self):
        self.user = UserFactory()
        self.distributor = DistributorFactory()
        ManufacturerFactory(name='Samsung')
        ManufacturerFactory(name='TDK')
        self.usd = CurrencyFactory(iso_code='USD')

        self.quotation_file = open(os.path.join(
            settings.APP_ROOT, 'tests/files/Quotation.csv'))

        self.data = {
            'distributor': self.distributor.pk,
            'ref_number': 'REF123',
            'issuance_date': now(),
            'expiry_date': now(),
            'is_completed': True,
            'quotation_file': SimpleUploadedFile('Quotation.csv',
                                                 self.quotation_file.read()),
        }

    def test_view(self):
        self.should_redirect_to_login_when_anonymous()

        self.is_callable(user=self.user)

        self.is_postable(user=self.user, data=self.data, to=self.get_url())

        self.assertEqual(Quotation.objects.count(), 1, msg=(
            'After a post with valid data, there should be one Quotation in'
            ' the database.'))
        self.assertEqual(QuotationItem.objects.count(), 2, msg=(
            'After a post with valid data, there should be four QuotationItems'
            ' in the database.'))
        self.assertEqual(Price.objects.count(), 4, msg=(
            'After a post with valid data, there should be three Prices in'
            ' the database.'))

        self.quotation_file.seek(0)
        self.data['quotation_file'] = SimpleUploadedFile(
            'Quotation.csv', self.quotation_file.read())
        self.is_postable(user=self.user, data=self.data, to=self.get_url())
        self.assertEqual(Quotation.objects.count(), 1, msg=(
            'After posting again, there should stil be one Quotation in the'
            ' database.'))
        self.assertEqual(QuotationItem.objects.count(), 2, msg=(
            'After posting again, there should still be four QuotationItems'
            ' in the database.'))
        self.assertEqual(Price.objects.count(), 4, msg=(
            'After posting again, there should still be three Prices in'
            ' the database.'))


class ReportViewTestCase(ViewRequestFactoryTestMixin, TestCase):
    """Tests for the ``ReportView`` view class."""
    longMessage = True
    view_class = views.ReportView

    def get_view_name(self):
        return 'aps_purchasing_report'

    def get_view_kwargs(self):
        return {'pk': self.bom.pk}

    def setUp(self):
        self.user = UserFactory()
        self.bom = BOMFactory()
        self.price = PriceFactory()
        self.item = self.price.quotation_item
        self.quotation = self.item.quotation

    def test_view(self):
        self.is_callable(user=self.user)
        self.is_callable(user=self.user, kwargs={})
        self.redirects(user=self.user, kwargs={}, data={
            'part_number': self.bom.ipn.code}, to=self.get_url())
        self.is_callable(user=self.user, kwargs={}, data={
            'part_number': 'wrongcode'})
