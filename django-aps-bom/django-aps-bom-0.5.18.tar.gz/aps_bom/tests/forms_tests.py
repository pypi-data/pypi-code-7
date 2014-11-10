"""Tests for the forms of the aps_bom app."""
import os

from django.conf import settings
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.test import TestCase
from django.utils.timezone import now

from ..forms import BOMUploadForm, CBOMUploadForm
from ..models import BOM, BOMItem, CBOM, CBOMItem, EPN
from .factories import (
    CompanyFactory,
    EPNFactory,
    IPNFactory,
    UnitFactory,
)


class BOMUploadFormTestCase(TestCase):
    """TestCase for the BOMUploadForm form class."""
    longMessage = True

    def setUp(self):
        self.unit = UnitFactory(code='pcs', description='pieces')

        self.ipn = IPNFactory()
        IPNFactory(code='7900.1500')

        self.csv_file = open(os.path.join(
            settings.APP_ROOT, 'tests/files/BOM.csv'))

        self.data = {
            'ipn': self.ipn.pk,
            'description': 'BOM description',
        }

        self.file_path = os.path.join(
            settings.APP_ROOT, 'tests/files/BOM.csv')
        self.csv_file = open(self.file_path)
        self.tmp = TemporaryUploadedFile('BOM.csv', 'text/csv', 0, None)
        self.tmp.write(self.csv_file.read())
        self.tmp.seek(0)
        self.tmp.size = os.path.getsize(self.file_path)

        self.files = {
            'csv_file': self.tmp,
        }

    def tearDown(self):
        self.csv_file.close()

    def test_form(self):
        bad_data = self.data.copy()
        bad_data.update({'ipn': ''})
        form = BOMUploadForm(data=bad_data, files=self.files)
        self.assertFalse(form.is_valid(), msg='The form should not be valid.')

        form = BOMUploadForm(data=self.data, files=self.files)
        self.assertFalse(form.is_valid(), msg=(
            'The form should not be valid, because not all IPNs are in the'
            ' database, yet.'))

        IPNFactory(code='6030.2345')
        form = BOMUploadForm(data=self.data, files=self.files)
        self.assertTrue(form.is_valid(), msg=(
            'The form should be valid once there are all EPNs in the database.'
            ' Errors: {0}'.format(form.errors)))

        form.save()
        self.assertEqual(BOM.objects.count(), 1, msg=(
            'Form save did not create the correct amount of BOMs.'))
        self.assertEqual(BOMItem.objects.count(), 2, msg=(
            'Form save did not create the correct amount of BOMItems.'))

        self.unit.delete()
        form = BOMUploadForm(data=self.data, files=self.files)
        self.assertFalse(form.is_valid(), msg=(
            'The form should not be valid, because not all units exist.'))


class CBOMUploadFormTestCase(TestCase):
    """TestCase for the CBOMUploadForm form class."""
    longMessage = True

    def setUp(self):
        self.customer = CompanyFactory()
        self.unit = UnitFactory(code='pcs', description='pieces')

        self.epn = EPNFactory(epn='945382', company=self.customer)

        self.data = {
            'customer': self.customer.id,
            'description': 'Description for the CBOM',
            'html_link': '',
            'product': 'This product is used here',
            'version_date': now(),
        }

        self.file_path = os.path.join(
            settings.APP_ROOT, 'tests/files/cBOM.csv')
        self.csv_file = open(self.file_path)
        self.tmp = TemporaryUploadedFile('cBOM.csv', 'text/csv', 0, None)
        self.tmp.write(self.csv_file.read())
        self.tmp.seek(0)
        self.tmp.size = os.path.getsize(self.file_path)

        self.files = {
            'csv_file': self.tmp,
        }

    def tearDown(self):
        self.csv_file.close()

    def test_form(self):
        bad_data = self.data.copy()
        bad_data.update({'description': ''})
        form = CBOMUploadForm(data=bad_data, files=self.files)
        self.assertFalse(form.is_valid(), msg=(
            'The form should not be valid, because not all EPNs are in the'
            ' database, yet.'))

        form = CBOMUploadForm(data=self.data, files=self.files)
        self.assertFalse(form.is_valid(), msg=(
            'The form should not be valid, because not all EPNs are in the'
            ' database, yet.'))

        epn = EPN.objects.get(epn='743629')
        form = CBOMUploadForm(data=self.data, files=self.files)
        self.assertFalse(form.is_valid(), msg=(
            'The form should not be valid, because the EPNs don\'t all have'
            ' IPN or CPN added.'))

        epn.ipn = IPNFactory()
        epn.cpn = IPNFactory()
        epn.save()
        form = CBOMUploadForm(data=self.data, files=self.files)
        self.assertTrue(form.is_valid(), msg=(
            'The form should be valid once there are all EPNs in the database.'
            ' Errors: {0}'.format(form.errors)))

        form.save()
        self.assertEqual(CBOM.objects.count(), 1, msg=(
            'Form save did not create the correct amount of CBOMs.'))
        self.assertEqual(CBOMItem.objects.count(), 2, msg=(
            'Form save did not create the correct amount of CBOMItems.'))

        self.unit.delete()
        form = CBOMUploadForm(data=self.data, files=self.files)
        self.assertFalse(form.is_valid(), msg=(
            'The form should not be valid, because not all units exist.'))
