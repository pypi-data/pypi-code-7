# from django.test import TestCase


# class MyTests(TestCase):
#     def test_views(self):
#         response = self.client.get("/factura_global_app/generar_factura_global")
#         self.assertEqual(response.status_code, 200)

import pytest

# models test
@pytest.mark.django_db
class RegistroAccesoTest:
	def test_view(self,client):
		response = client.get('/factura_global_app/generar_factura_global')
		assert response.status_code == 200