# from django.test import TestCase
# from .models import RegistroAcceso
# import datetime
# from django.core.urlresolvers import reverse
# from .forms import RegistroAc0cesoForm
import pytest
from django.test import Client

# models test
@pytest.mark.django_db
class TestFacturas:
	urls = 'django_microsip_base.test_urls'

	def test_view(self):
		x=200
		assert x == 200

	def test_with_client(self):
		c = Client()
		response = c.get('/')
		assert response.status_code == 200

    # def create_RegistroAcceso(self, id=1,cliente=352,acceso='S',fecha=datetime.datetime.now().date,hora=datetime.datetime.now().time):
    #     return RegistroAcceso.objects.create(id=id,cliente=cliente,acceso=acceso,fecha=fecha,hora=hora)

    # def test_RegistroAcceso_creation(self):
    #     r = self.create_RegistroAcceso()
    #     self.assertTrue(isinstance(r, RegistroAcceso))
    #     self.assertEqual(r.__unicode__(), r.title)