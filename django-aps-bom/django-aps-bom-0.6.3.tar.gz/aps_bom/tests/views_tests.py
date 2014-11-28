"""Tests for the views of the aps_bom app."""
import os

from django.conf import settings
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.test import TestCase

from django_libs.tests.mixins import ViewTestMixin, ViewRequestFactoryTestMixin
from django_libs.tests.factories import UserFactory

from .. import views
from . import factories


class DropDownChoicesAJAXViewTestCase(ViewRequestFactoryTestMixin, TestCase):
    """Tests for the ``DropDownChoicesAJAXView`` view class."""
    view_class = views.DropDownChoicesAJAXView

    def setUp(self):
        self.user = UserFactory()
        self.company = factories.CompanyFactory()
        self.epn = factories.EPNFactory(company=self.company)
        self.data = {
            'action': 'get_epn_choices_for_customer',
            'obj_id': self.company.id,
        }

    def test_view(self):
        self.should_redirect_to_login_when_anonymous()
        self.is_not_callable(user=self.user)
        self.is_callable(user=self.user, ajax=True, data=self.data)


class BOMUploadViewTestCase(ViewTestMixin, TestCase):
    """Tests for the ``BOMUploadView`` view class."""
    longMessage = True

    def get_view_name(self):
        return 'aps_bom_bom_upload'

    def get_login_url(self):
        return settings.LOGIN_URL

    def setUp(self):
        self.user = UserFactory()
        self.unit = factories.UnitFactory(code='pcs', description='pieces')

        self.ipn = factories.IPNFactory()
        factories.IPNFactory(code='7900.1500')
        factories.IPNFactory(code='6030.2345')

        self.file_path = os.path.join(
            settings.APP_ROOT, 'tests/files/BOM.csv')
        self.csv_file = open(self.file_path)
        self.tmp = TemporaryUploadedFile('BOM.csv', 'text/csv', 0, None)
        self.tmp.write(self.csv_file.read())
        self.tmp.seek(0)
        self.tmp.size = os.path.getsize(self.file_path)

        self.data = {
            'ipn': self.ipn.pk,
            'description': 'Test description for BOM',
            'csv_file': self.tmp,
        }

    def tearDown(self):
        self.csv_file.close()

    def test_view(self):
        self.should_redirect_to_login_when_anonymous()
        self.should_be_callable_when_authenticated(self.user)
        self.is_callable(method='post', data=self.data)


class CBOMDownloadViewTestCase(ViewTestMixin, TestCase):
    """Tests for the ``CBOMDownloadView`` view class."""
    longMessage = True

    def get_login_url(self):
        return settings.LOGIN_URL

    def get_view_kwargs(self):
        return {'cbom_pk': self.cbom.pk}

    def get_view_name(self):
        return 'aps_bom_cbom_download'

    def setUp(self):
        self.user = UserFactory()
        self.cbom = factories.CBOMFactory()

    def test_view(self):
        self.should_redirect_to_login_when_anonymous()
        self.should_be_callable_when_authenticated(self.user)
        self.is_not_callable(kwargs={'cbom_pk': 123}, message=(
            'With the wrong kwargs, the view should not be callable.'))
        self.is_callable(kwargs={}, message=(
            'Even without kwargs, the view should be callable.'))


class CBOMUploadViewTestCase(ViewTestMixin, TestCase):
    """Tests for the ``CBOMUploadView`` view class."""
    longMessage = True

    def get_view_name(self):
        return 'aps_bom_cbom_upload'

    def get_login_url(self):
        return settings.LOGIN_URL

    def setUp(self):
        self.user = UserFactory()
        self.customer = factories.CompanyFactory()
        self.unit = factories.UnitFactory(code='pcs', description='pieces')

        factories.EPNFactory(epn='945382', company=self.customer)
        factories.EPNFactory(epn='743629', company=self.customer)

        self.file_path = os.path.join(
            settings.APP_ROOT, 'tests/files/cBOM.csv')
        self.csv_file = open(self.file_path)
        self.tmp = TemporaryUploadedFile('cBOM.csv', 'text/csv', 0, None)
        self.tmp.write(self.csv_file.read())
        self.tmp.seek(0)
        self.tmp.size = os.path.getsize(self.file_path)

        self.data = {
            'customer': self.customer.id,
            'description': 'Description for the CBOM',
            'html_link': '',
            'product': 'This product is used here',
            'version_date': '12/12/2012',
            'csv_file': self.tmp,
        }

    def tearDown(self):
        self.csv_file.close()

    def test_view(self):
        self.should_redirect_to_login_when_anonymous()
        self.should_be_callable_when_authenticated(self.user)
        self.is_callable(method='post', data=self.data)
