# -*- coding: utf-8 -*-
import six
import unittest
from freezegun import freeze_time
from datetime import datetime
import requests

import api_toolkit

from emites_api.main import Emites, Nfse, Batch
from .helpers import (
    use_cassette as use_emites_cassette, APP_CREDENTIALS,
    TEST_EMITTER, TEST_TAKER, TEST_SERVICE_VALUE, TEST_NFSE
)

__all__ = [
    'EmitesTest', 'EmittersTest', 'TakersTest',
    'ServiceValuesTest', 'NfseTest', 'NfseConstantsTest', 'BatchesTest'
]


class WithFrozenTime(unittest.TestCase):

    def setUp(self):
        self.freezer = freeze_time("2014-02-19 19:04:00")
        self.freezer.start()

    def tearDown(self):
        self.freezer.stop()


class EmitesTest(unittest.TestCase):

    def setUp(self):
        with use_emites_cassette('collections_options'):
            self.api_client = Emites(**APP_CREDENTIALS)

    def test_instance_has_emitters_takers_servicevalues_nfse_and_batches(self):
        self.assertTrue(hasattr(self.api_client, 'emitters'))
        self.assertTrue(isinstance(self.api_client.emitters, api_toolkit.Collection))

        self.assertTrue(hasattr(self.api_client, 'takers'))
        self.assertTrue(isinstance(self.api_client.takers, api_toolkit.Collection))

        self.assertTrue(hasattr(self.api_client, 'service_values'))
        self.assertTrue(isinstance(self.api_client.service_values, api_toolkit.Collection))

        self.assertTrue(hasattr(self.api_client, 'nfse'))
        self.assertTrue(isinstance(self.api_client.nfse, api_toolkit.Collection))

        self.assertTrue(hasattr(self.api_client, 'batches'))
        self.assertTrue(isinstance(self.api_client.batches, api_toolkit.Collection))


class EmittersTest(unittest.TestCase):

    def setUp(self):
        self.post_data = TEST_EMITTER.copy()
        with use_emites_cassette('collections_options'):
            self.api_client = Emites(**APP_CREDENTIALS)

    def test_emitters_are_a_collection(self):
        self.assertTrue(isinstance(self.api_client.emitters, api_toolkit.Collection))

    def test_emitters_are_iterable(self):
        with use_emites_cassette('emitters/list'):
            emitters = [item for item in self.api_client.emitters.all()]

    def test_emitters_can_be_created(self):
        with use_emites_cassette('emitters/create'):
            emitter = self.api_client.emitters.create(**self.post_data)

        self.assertEqual(emitter.id, 12)
        self.assertEqual(emitter.email, self.post_data['email'])
        self.assertEqual(emitter.account_id, 56)

    def test_creation_without_email_fails(self):
        del(self.post_data['email'])
        with use_emites_cassette('emitters/create_without_email'):
            self.assertRaises(requests.HTTPError, self.api_client.emitters.create, **self.post_data)

    def test_creation_without_social_reason_fails(self):
        del(self.post_data['social_reason'])
        with use_emites_cassette('emitters/create_without_social_reason'):
            self.assertRaises(requests.HTTPError, self.api_client.emitters.create, **self.post_data)

    def test_creation_without_cnpj_fails(self):
        del(self.post_data['cnpj'])
        with use_emites_cassette('emitters/create_without_cnpj'):
            self.assertRaises(requests.HTTPError, self.api_client.emitters.create, **self.post_data)

    def test_creation_without_fancy_name_fails(self):
        del(self.post_data['fancy_name'])
        with use_emites_cassette('emitters/create_without_fancy_name'):
            self.assertRaises(requests.HTTPError, self.api_client.emitters.create, **self.post_data)

    def test_creation_without_city_inscription_fails(self):
        del(self.post_data['city_inscription'])
        with use_emites_cassette('emitters/create_without_city_inscription'):
            self.assertRaises(requests.HTTPError, self.api_client.emitters.create, **self.post_data)

    def test_creation_without_state_fails(self):
        del(self.post_data['state'])
        with use_emites_cassette('emitters/create_without_state'):
            self.assertRaises(requests.HTTPError, self.api_client.emitters.create, **self.post_data)

    def test_creation_without_city_fails(self):
        del(self.post_data['city'])
        with use_emites_cassette('emitters/create_without_city'):
            self.assertRaises(requests.HTTPError, self.api_client.emitters.create, **self.post_data)

    def test_creation_without_neighborhood_fails(self):
        del(self.post_data['neighborhood'])
        with use_emites_cassette('emitters/create_without_neighborhood'):
            self.assertRaises(requests.HTTPError, self.api_client.emitters.create, **self.post_data)

    def test_creation_without_street_type_does_not_fail(self):
        del(self.post_data['street_type'])
        with use_emites_cassette('emitters/create_without_street_type'):
            emitter = self.api_client.emitters.create(**self.post_data)

        self.assertEqual(emitter.id, 13)
        self.assertEqual(emitter.email, self.post_data['email'])
        self.assertEqual(emitter.account_id, 56)

    def test_creation_without_street_fails(self):
        del(self.post_data['street'])
        with use_emites_cassette('emitters/create_without_street'):
            self.assertRaises(requests.HTTPError, self.api_client.emitters.create, **self.post_data)

    def test_creation_without_number_fails(self):
        del(self.post_data['number'])
        with use_emites_cassette('emitters/create_without_number'):
            self.assertRaises(requests.HTTPError, self.api_client.emitters.create, **self.post_data)

    def test_creation_without_zip_code_fails(self):
        del(self.post_data['zip_code'])
        with use_emites_cassette('emitters/create_without_zip_code'):
            self.assertRaises(requests.HTTPError, self.api_client.emitters.create, **self.post_data)

    def test_creation_without_phone_fails(self):
        del(self.post_data['phone'])
        with use_emites_cassette('emitters/create_without_phone'):
            self.assertRaises(requests.HTTPError, self.api_client.emitters.create, **self.post_data)

    def test_creation_without_certificate_fails(self):
        del(self.post_data['certificate'])
        with use_emites_cassette('emitters/create_without_certificate'):
            self.assertRaises(requests.HTTPError, self.api_client.emitters.create, **self.post_data)

    def test_creation_without_password_fails(self):
        del(self.post_data['password'])
        with use_emites_cassette('emitters/create_without_password'):
            self.assertRaises(requests.HTTPError, self.api_client.emitters.create, **self.post_data)

    def test_get_emitter_from_another_account_fails(self):
        with use_emites_cassette('emitters/get_from_another_account'):
            self.assertRaises(requests.HTTPError, self.api_client.emitters.get, 2)

    def test_get_emitter_from_this_account_works(self):
        with use_emites_cassette('emitters/get_from_this_account'):
            emitter = self.api_client.emitters.get(12)

        self.assertEqual(emitter.email, self.post_data['email'])
        self.assertEqual(emitter.account_id, 56)

    def test_emitters_can_be_updated(self):
        # Using PUT
        with use_emites_cassette('emitters/get_from_this_account'):
            emitter = self.api_client.emitters.get(12)

        emitter.city_inscription = '1111111'
        emitter.resource_data['password'] = self.post_data['password']
        emitter.resource_data['certificate'] = self.post_data['certificate']
        with use_emites_cassette('emitters/update_city_inscription'):
            updated_emitter = emitter.save()

        self.assertEqual(updated_emitter.city_inscription, '1111111')

    def test_emitters_can_be_deleted(self):
        with use_emites_cassette('emitters/get_from_this_account'):
            emitter = self.api_client.emitters.get(12)

        with use_emites_cassette('emitters/delete'):
            emitter.delete()

        with use_emites_cassette('emitters/list_after_deletion'):
            emitters = [item for item in self.api_client.emitters.all()]

        self.assertEqual(emitters, [])


class TakersTest(unittest.TestCase):

    def setUp(self):
        self.post_data = TEST_TAKER.copy()
        self.post_data['address'] = TEST_TAKER['address'].copy()
        self.post_data['contact'] = TEST_TAKER['contact'].copy()
        with use_emites_cassette('collections_options'):
            self.api_client = Emites(**APP_CREDENTIALS)

    def test_takers_are_a_collection(self):
        self.assertTrue(isinstance(self.api_client.takers, api_toolkit.Collection))

    def test_takers_are_iterable(self):
        with use_emites_cassette('takers/list'):
            takers = [item for item in self.api_client.takers.all()]

    def test_takers_can_be_created(self):
        with use_emites_cassette('takers/create'):
            taker = self.api_client.takers.create(**self.post_data)

        self.assertEqual(taker.id, 11)
        self.assertEqual(taker.cnpj, self.post_data['cnpj'])
        self.assertEqual(taker.account_id, 56)

    def test_creation_without_cnpj_or_cpf_fails(self):
        del(self.post_data['cnpj'])
        with use_emites_cassette('takers/create_without_cnpj'):
            self.assertRaises(requests.HTTPError, self.api_client.takers.create, **self.post_data)

    def test_creation_with_cnpj_and_cpf_fails(self):
        self.post_data['cpf'] = '11111111111'
        with use_emites_cassette('takers/create_with_cpf_and_cnpj'):
            self.assertRaises(requests.HTTPError, self.api_client.takers.create, **self.post_data)

    def test_creation_without_fancy_name_does_not_fail(self):
        del(self.post_data['fancy_name'])
        self.post_data['cnpj'] = '57721546000159'
        with use_emites_cassette('takers/create_without_fancy_name'):
            taker = self.api_client.takers.create(**self.post_data)

        self.assertEqual(taker.id, 12)
        self.assertEqual(taker.cnpj, self.post_data['cnpj'])
        self.assertEqual(taker.account_id, 56)

    def test_creation_without_social_reason_fails(self):
        del(self.post_data['social_reason'])
        with use_emites_cassette('takers/create_without_social_reason'):
            self.assertRaises(requests.HTTPError, self.api_client.takers.create, **self.post_data)

    def test_creation_without_address_fails(self):
        del(self.post_data['address'])
        with use_emites_cassette('takers/create_without_address'):
            self.assertRaises(requests.HTTPError, self.api_client.takers.create, **self.post_data)

    def test_creation_without_street_fails(self):
        del(self.post_data['address']['street'])
        with use_emites_cassette('takers/create_without_street'):
            self.assertRaises(requests.HTTPError, self.api_client.takers.create, **self.post_data)

    def test_creation_without_number_fails(self):
        del(self.post_data['address']['number'])
        with use_emites_cassette('takers/create_without_number'):
            self.assertRaises(requests.HTTPError, self.api_client.takers.create, **self.post_data)

    def test_creation_without_neighborhood_fails(self):
        del(self.post_data['address']['neighborhood'])
        with use_emites_cassette('takers/create_without_neighborhood'):
            self.assertRaises(requests.HTTPError, self.api_client.takers.create, **self.post_data)

    def test_creation_without_city_code_fails(self):
        del(self.post_data['address']['city_code'])
        with use_emites_cassette('takers/create_without_city_code'):
            self.assertRaises(requests.HTTPError, self.api_client.takers.create, **self.post_data)

    def test_creation_without_state_fails(self):
        del(self.post_data['address']['state'])
        with use_emites_cassette('takers/create_without_state'):
            self.assertRaises(requests.HTTPError, self.api_client.takers.create, **self.post_data)

    def test_creation_without_zip_code_fails(self):
        del(self.post_data['address']['zip_code'])
        with use_emites_cassette('takers/create_without_zip_code'):
            self.assertRaises(requests.HTTPError, self.api_client.takers.create, **self.post_data)

    def test_creation_without_neighborhood_type_does_not_fail(self):
        del(self.post_data['address']['neighborhood_type'])
        self.post_data['cnpj'] = '32929662000137'
        with use_emites_cassette('takers/create_without_neighborhood_type'):
            taker = self.api_client.takers.create(**self.post_data)

        self.assertEqual(taker.id, 13)
        self.assertEqual(taker.cnpj, self.post_data['cnpj'])
        self.assertEqual(taker.account_id, 56)

    def test_creation_without_city_fails(self):
        del(self.post_data['address']['city'])
        with use_emites_cassette('takers/create_without_city'):
            self.assertRaises(requests.HTTPError, self.api_client.takers.create, **self.post_data)

    def test_creation_without_contact_fails(self):
        del(self.post_data['contact'])
        with use_emites_cassette('takers/create_without_contact'):
            self.assertRaises(requests.HTTPError, self.api_client.takers.create, **self.post_data)

    def test_creation_without_phone_fails(self):
        del(self.post_data['contact']['phone'])
        with use_emites_cassette('takers/create_without_phone'):
            self.assertRaises(requests.HTTPError, self.api_client.takers.create, **self.post_data)

    def test_creation_without_email_does_not_fail(self):
        del(self.post_data['contact']['email'])
        self.post_data['cnpj'] = '81162077000160'
        with use_emites_cassette('takers/create_without_email'):
            taker = self.api_client.takers.create(**self.post_data)

        self.assertEqual(taker.id, 14)
        self.assertEqual(taker.cnpj, self.post_data['cnpj'])
        self.assertEqual(taker.account_id, 56)

    def test_get_taker_from_another_account_fails(self):
        with use_emites_cassette('takers/get_from_another_account'):
            self.assertRaises(requests.HTTPError, self.api_client.takers.get, 2)

    def test_get_taker_from_this_account_works(self):
        with use_emites_cassette('takers/get_from_this_account'):
            taker = self.api_client.takers.get(10)

        self.assertEqual(taker.cnpj, self.post_data['cnpj'])
        self.assertEqual(taker.account_id, 56)

    def test_takers_can_be_updated(self):
        # Using PUT
        with use_emites_cassette('takers/get_from_this_account'):
            taker = self.api_client.takers.get(10)

        taker.city_inscription = '1111111'
        with use_emites_cassette('takers/update_city_inscription'):
            updated_taker = taker.save()

        self.assertEqual(updated_taker.city_inscription, '1111111')

    def test_takers_can_be_deleted(self):
        with use_emites_cassette('takers/get_from_this_account'):
            taker = self.api_client.takers.get(10)

        with use_emites_cassette('takers/delete'):
            taker.delete()

        with use_emites_cassette('takers/list_after_deletion'):
            takers = [item for item in self.api_client.takers.all()]

        self.assertEqual(takers, [])


class ServiceValuesTest(unittest.TestCase):

    def setUp(self):
        with use_emites_cassette('collections_options'):
            self.api_client = Emites(**APP_CREDENTIALS)

        with use_emites_cassette('emitters/get_from_this_account'):
            self.emitter = self.api_client.emitters.get(12)

        self.post_data = TEST_SERVICE_VALUE.copy()
        self.post_data['emitter_id'] = self.emitter.id

    def test_service_values_are_a_collection(self):
        self.assertTrue(isinstance(self.api_client.service_values, api_toolkit.Collection))

    def test_service_values_are_iterable(self):
        with use_emites_cassette('service_values/list'):
            service_values = [item for item in self.api_client.service_values.all()]

    def test_service_values_can_be_created(self):
        with use_emites_cassette('service_values/create'):
            service_value = self.api_client.service_values.create(**self.post_data)

        self.assertEqual(service_value.id, 39)
        self.assertEqual(service_value.emitter_id, self.emitter.id)
        self.assertEqual(service_value.name, self.post_data['name'])
        self.assertEqual(service_value.service_amount, self.post_data['service_amount'])
        self.assertEqual(service_value.iss_percentage, self.post_data['iss_percentage'])

    def test_service_values_can_be_created_with_only_name_and_emitter_id(self):
        del(self.post_data['service_amount'])
        del(self.post_data['iss_percentage'])
        with use_emites_cassette('service_values/create_with_minimal_data'):
            service_value = self.api_client.service_values.create(**self.post_data)

        self.assertEqual(service_value.id, 38)
        self.assertEqual(service_value.emitter_id, self.emitter.id)
        self.assertEqual(service_value.name, self.post_data['name'])
        self.assertEqual(service_value.service_amount, None)
        self.assertEqual(service_value.iss_percentage, None)

    def test_creation_without_name_fails(self):
        del(self.post_data['name'])
        with use_emites_cassette('service_values/create_without_name'):
            self.assertRaises(requests.HTTPError, self.api_client.service_values.create, **self.post_data)

    def test_creation_without_emitter_id_fails(self):
        del(self.post_data['emitter_id'])
        with use_emites_cassette('service_values/create_without_emitter_id'):
            self.assertRaises(requests.HTTPError, self.api_client.service_values.create, **self.post_data)

    def test_get_service_value_from_another_account_fails(self):
        with use_emites_cassette('service_values/get_from_another_account'):
            self.assertRaises(requests.HTTPError, self.api_client.service_values.get, 2)

    def test_get_service_value_from_this_account_works(self):
        with use_emites_cassette('service_values/get_from_this_account'):
            service_value = self.api_client.service_values.get(38)

        self.assertEqual(service_value.emitter_id, self.post_data['emitter_id'])
        self.assertEqual(service_value.id, 38)

    def test_service_values_can_be_updated(self):
        # Using PUT
        with use_emites_cassette('service_values/get_from_this_account'):
            service_value = self.api_client.service_values.get(38)

        service_value.iss_percentage = '0.5'
        service_value.description = u'Teste da api de alteração de dados de valores de serviço'
        with use_emites_cassette('service_values/update_iss_percentage_and_description'):
            updated_service_value = service_value.save()

        self.assertEqual(updated_service_value.iss_percentage, '0.5')
        self.assertEqual(updated_service_value.description, service_value.description)

    def test_service_values_can_be_deleted(self):
        with use_emites_cassette('service_values/get_from_this_account'):
            service_value = self.api_client.service_values.get(38)

        with use_emites_cassette('service_values/delete'):
            service_value.delete()

        with use_emites_cassette('service_values/list_after_deletion'):
            service_values = [item for item in self.api_client.service_values.all()]

        self.assertEqual(service_values, [])


class NfseTest(WithFrozenTime):

    def setUp(self):
        super(NfseTest, self).setUp()

        with use_emites_cassette('collections_options'):
            self.api_client = Emites(**APP_CREDENTIALS)

        with use_emites_cassette('emitters/get_from_this_account'):
            self.emitter = self.api_client.emitters.get(13)

        with use_emites_cassette('takers/get_from_this_account'):
            self.taker = self.api_client.takers.get(11)

        with use_emites_cassette('service_values/get_from_this_account'):
            self.service_values = self.api_client.service_values.get(39)

        self.post_data = TEST_NFSE.copy()
        self.post_data['emission_date'] = datetime.now().isoformat()
        self.post_data['emitter_id'] = self.emitter.id
        self.post_data['taker_id'] = self.taker.id
        self.post_data['service_values'] = TEST_NFSE['service_values'].copy()

    def test_nfse_are_a_collection(self):
        self.assertTrue(isinstance(self.api_client.nfse, api_toolkit.Collection))

    def test_nfse_are_iterable(self):
        with use_emites_cassette('nfse/list'):
            nfse = [item for item in self.api_client.nfse.all()]

    def test_nfse_can_be_created(self):
        with use_emites_cassette('nfse/create'):
            nfse = self.api_client.nfse.create(**self.post_data)

        self.assertEqual(nfse.id, 77)
        self.assertEqual(nfse.emitter_id, self.emitter.id)
        self.assertEqual(nfse.serie, self.post_data['serie'])

    def test_creation_with_emitter_from_another_account_fails(self):
        self.post_data['emitter_id'] = 2
        with use_emites_cassette('nfse/create_with_emitter_from_another_account'):
            self.assertRaises(requests.HTTPError, self.api_client.nfse.create, **self.post_data)

    def test_creation_with_taker_from_another_account_fails(self):
        self.post_data['taker_id'] = 2
        with use_emites_cassette('nfse/create_with_taker_from_another_account'):
            self.assertRaises(requests.HTTPError, self.api_client.nfse.create, **self.post_data)

    def test_creation_with_service_values_from_another_account_fails(self):
        self.post_data['service_values']['id'] = 2
        with use_emites_cassette('nfse/create_with_service_values_from_another_account'):
            self.assertRaises(requests.HTTPError, self.api_client.nfse.create, **self.post_data)

    def test_creation_without_service_values_service_amount_fails(self):
        del(self.post_data['service_values']['service_amount'])
        with use_emites_cassette('nfse/create_without_service_amount'):
            self.assertRaises(requests.HTTPError, self.api_client.nfse.create, **self.post_data)

    def test_creation_without_service_values_iss_percentage_fails(self):
        del(self.post_data['service_values']['iss_percentage'])
        with use_emites_cassette('nfse/create_without_iss_percentage'):
            self.assertRaises(requests.HTTPError, self.api_client.nfse.create, **self.post_data)

    def test_creation_without_service_values_service_item_code_fails(self):
        del(self.post_data['service_values']['service_item_code'])
        with use_emites_cassette('nfse/create_without_service_item_code'):
            self.assertRaises(requests.HTTPError, self.api_client.nfse.create, **self.post_data)

    def test_creation_without_service_values_city_code_fails(self):
        del(self.post_data['service_values']['city_code'])
        with use_emites_cassette('nfse/create_without_city_code'):
            self.assertRaises(requests.HTTPError, self.api_client.nfse.create, **self.post_data)

    def test_creation_without_service_values_description_fails(self):
        del(self.post_data['service_values']['description'])
        with use_emites_cassette('nfse/create_without_description'):
            self.assertRaises(requests.HTTPError, self.api_client.nfse.create, **self.post_data)

    def test_creation_without_service_values_iss_amount_does_not_fail(self):
        del(self.post_data['service_values']['iss_amount'])
        with use_emites_cassette('nfse/create_without_iss_amount'):
            nfse = self.api_client.nfse.create(**self.post_data)

        self.assertEqual(nfse.id, 317)
        self.assertEqual(nfse.service_values['iss_amount'], '4.99')

    def test_creation_without_service_values_nfse_liquid_amount_does_not_fail(self):
        del(self.post_data['service_values']['nfse_liquid_amount'])
        with use_emites_cassette('nfse/create_without_nfse_liquid_amount'):
            nfse = self.api_client.nfse.create(**self.post_data)

        self.assertEqual(nfse.id, 318)
        self.assertEqual(nfse.service_values['nfse_liquid_amount'], nfse.service_values['service_amount'])

    def test_creation_without_service_values_city_tax_code_does_not_fail(self):
        del(self.post_data['service_values']['city_tax_code'])
        with use_emites_cassette('nfse/create_without_city_tax_code'):
            nfse = self.api_client.nfse.create(**self.post_data)

        self.assertEqual(nfse.id, 319)
        self.assertEqual(nfse.service_values['city_tax_code'], None)

    def test_creation_without_service_values_cnae_code_does_not_fail(self):
        del(self.post_data['service_values']['cnae_code'])
        with use_emites_cassette('nfse/create_without_cnae_code'):
            nfse = self.api_client.nfse.create(**self.post_data)

        self.assertEqual(nfse.id, 320)
        self.assertEqual(nfse.service_values['cnae_code'], None)

    def test_creation_without_service_values_deduction_amount_does_not_fail(self):
        del(self.post_data['service_values']['deduction_amount'])
        with use_emites_cassette('nfse/create_without_deduction_amount'):
            nfse = self.api_client.nfse.create(**self.post_data)

        self.assertEqual(nfse.id, 321)
        self.assertEqual(nfse.service_values['deduction_amount'], '0.0')

    def test_creation_without_service_values_discount_conditioning_amount_fails(self):
        del(self.post_data['service_values']['discount_conditioning_amount'])
        with use_emites_cassette('nfse/create_without_discount_conditioning_amount'):
            nfse = self.api_client.nfse.create(**self.post_data)

        self.assertEqual(nfse.id, 322)
        self.assertEqual(nfse.service_values['discount_conditioning_amount'], '0')

    def test_creation_without_service_values_calculation_base_does_not_fail(self):
        del(self.post_data['service_values']['calculation_base'])
        with use_emites_cassette('nfse/create_without_calculation_base'):
            nfse = self.api_client.nfse.create(**self.post_data)

        self.assertEqual(nfse.id, 323)
        self.assertEqual(nfse.service_values['calculation_base'], nfse.service_values['service_amount'])

    def test_creation_with_taker_information(self):
        del(self.post_data['taker_id'])
        self.post_data['taker'] = {
            'address': {
                'city': u'Rio de Janeiro',
                'city_code': 3304557,
                'complement': u'11º andar',
                'country': u'Brasil',
                'country_abbreviation': u'BR',
                'country_code': u'01058',
                'neighborhood': u'Centro',
                'neighborhood_type': u'COM',
                'number': u'1142',
                'reference_point': u'Ao lado',
                'state': u'RJ',
                'street': u'dos testes',
                'street_type': u'AVN',
                'zip_code': u'20011020'
            },
            'city_inscription': u'00000000',
            'cnpj': u'91762868000184',
            'contact': {
                'email': u'pagamentos@python-emites.test',
                'phone': u'21000000000'
            },
            'cpf': None,
            'fancy_name': u'Empresa de Testes',
            'foreign_taker': False,
            'social_reason': u'Empresa de Testes Ltda ME',
            'special_situation': 0,
            'state_inscription': u'ISENTO',
            'substitute_state_inscription': None
        }
        with use_emites_cassette('nfse/create_with_taker_information'):
            nfse = self.api_client.nfse.create(**self.post_data)

        self.assertEqual(nfse.id, 80)
        self.assertEqual(nfse.taker, self.post_data['taker'])

    def test_taker_information_from_response(self):
        with use_emites_cassette('nfse/create'):
            nfse = self.api_client.nfse.create(**self.post_data)

        self.assertEqual(nfse.id, 77)
        expected_taker = {
            'address': {
                'city': u'Rio de Janeiro',
                'city_code': 3304557,
                'complement': None,
                'country': u'Brasil',
                'country_abbreviation': u'BR',
                'country_code': u'01058',
                'neighborhood': u'Centro',
                'neighborhood_type': u'COM',
                'number': u'42',
                'reference_point': None,
                'state': u'RJ',
                'street': u'dos testes',
                'street_type': u'RUA',
                'zip_code': u'20011020'
            },
            'city_inscription': u'00000000',
            'cnpj': u'91762868000184',
            'contact': {
                'email': u'financeiro@python-emites.test',
                'phone': u'21000000000'
            },
            'cpf': None,
            'fancy_name': u'Empresa de Testes',
            'foreign_taker': False,
            'social_reason': u'Empresa de Testes Ltda ME',
            'special_situation': 0,
            'state_inscription': u'ISENTO',
            'substitute_state_inscription': None
        }
        self.assertEqual(nfse.taker, expected_taker)

    def test_creation_with_merged_service_values_data(self):
        self.post_data['service_values']['id'] = self.service_values.id
        del(self.post_data['service_values']['service_amount'])
        del(self.post_data['service_values']['iss_percentage'])
        with use_emites_cassette('nfse/create_with_merged_service_values_data'):
            nfse = self.api_client.nfse.create(**self.post_data)

        self.assertEqual(nfse.id, 81)
        expected_service_values = {
            'calculation_base': u'99.99',
            'city_code': 3304557,
            'city_tax_code': u'010501',
            'cnae_code': u'6201-5',
            'cofins_amount': None,
            'csll_amount': None,
            'deduction_amount': u'0.00',
            'description': u'Testes da api do emites',
            'discount_conditioning_amount': u'0.00',
            'inss_amount': None,
            'ir_amount': None,
            'iss_amount': u'4.99',
            'iss_percentage': u'5.00',
            'nfse_liquid_amount': u'99.99',
            'other_retentions': None,
            'pis_amount': None,
            'retained_iss': False,
            'retained_iss_amount': None,
            'service_amount': u'99.99',
            'service_item_code': u'0105',
            'unconditioned_discount': None
        }
        self.assertEqual(nfse.service_values, expected_service_values)

    def test_service_values_from_response(self):
        with use_emites_cassette('nfse/create'):
            nfse = self.api_client.nfse.create(**self.post_data)

        self.assertEqual(nfse.id, 77)
        expected_service_values = {
            'calculation_base': u'99.99',
            'city_code': 3304557,
            'city_tax_code': u'010501',
            'cnae_code': u'6201-5',
            'cofins_amount': None,
            'csll_amount': None,
            'deduction_amount': u'0.00',
            'description': u'Testes da api do emites',
            'discount_conditioning_amount': u'0.00',
            'inss_amount': None,
            'ir_amount': None,
            'iss_amount': u'4.99',
            'iss_percentage': u'5.00',
            'nfse_liquid_amount': u'99.99',
            'other_retentions': None,
            'pis_amount': None,
            'retained_iss': False,
            'retained_iss_amount': None,
            'service_amount': u'99.99',
            'service_item_code': u'0105',
            'unconditioned_discount': None
        }
        self.assertEqual(nfse.service_values, expected_service_values)

    def test_get_nfse_from_another_account_fails(self):
        with use_emites_cassette('nfse/get_from_another_account'):
            self.assertRaises(requests.HTTPError, self.api_client.nfse.get, 2)

    def test_get_nfse_from_this_account_works(self):
        with use_emites_cassette('nfse/get_from_this_account'):
            nfse = self.api_client.nfse.get(77)

        self.assertEqual(nfse.emitter_id, self.post_data['emitter_id'])
        self.assertEqual(nfse.id, 77)

    def test_nfse_cannot_be_updated(self):
        with use_emites_cassette('nfse/get_from_this_account'):
            nfse = self.api_client.nfse.get(77)

        nfse.service_values['iss_percentage'] = '0.3'
        nfse.service_values['description'] = u'Teste da api de alteração de dados de valores de serviço'
        self.assertRaises(ValueError, nfse.save)

    def test_nfse_cannot_be_deleted(self):
        with use_emites_cassette('nfse/get_from_this_account'):
            nfse = self.api_client.nfse.get(77)

        with use_emites_cassette('nfse/delete'):
            self.assertRaises(requests.HTTPError, nfse.delete)

    def test_nfse_can_be_created_inside_a_batch(self):
        with use_emites_cassette('batches/get_from_this_account'):
            batch = self.api_client.batches.get(24)

        self.post_data = TEST_NFSE.copy()
        self.post_data['emission_date'] = datetime.now().isoformat()
        self.post_data['emitter_id'] = self.emitter.id
        self.post_data['taker_id'] = self.taker.id
        self.post_data['batch_id'] = batch.id
        self.post_data['service_values'] = TEST_NFSE['service_values'].copy()

        with use_emites_cassette('nfse/create_in_a_batch'):
            nfse = self.api_client.nfse.create(**self.post_data)

        self.assertEqual(nfse.id, 86)
        self.assertEqual(nfse.emitter_id, self.emitter.id)
        self.assertEqual(nfse.serie, self.post_data['serie'])

    def test_nfse_can_be_deleted_from_a_pending_batch(self):
        with use_emites_cassette('batches/get_from_this_account'):
            batch = self.api_client.batches.get(24)

        self.post_data = TEST_NFSE.copy()
        self.post_data['emission_date'] = datetime.now().isoformat()
        self.post_data['emitter_id'] = self.emitter.id
        self.post_data['taker_id'] = self.taker.id
        self.post_data['batch_id'] = batch.id
        self.post_data['service_values'] = TEST_NFSE['service_values'].copy()
        self.post_data['service_values']['iss_percentage'] = '0.01'

        with use_emites_cassette('nfse/create_in_a_batch'):
            nfse = self.api_client.nfse.create(**self.post_data)
        self.assertEqual(nfse.id, 87)

        with use_emites_cassette('nfse/delete_in_a_batch'):
            nfse.load_options()
            nfse.delete()

        with use_emites_cassette('nfse/get_removed_nfse'):
            self.assertRaises(requests.HTTPError, self.api_client.nfse.get, 87)

    def test_nfses_have_its_own_class(self):
        with use_emites_cassette('nfse/get_from_this_account'):
            nfse = self.api_client.nfse.get(77)

        self.assertTrue(isinstance(nfse, Nfse))

    def test_nfses_have_a_history(self):
        with use_emites_cassette('nfse/get_from_this_account'):
            nfse = self.api_client.nfse.get(77)

        with use_emites_cassette('nfse/history'):
            events = [item for item in nfse.history.all()]

        self.assertEqual(len(events), 2)
        first_event = {
            'account': {'id': 56, 'name': u'python-emites'},
            'date': u'2014-11-11T18:35:23.621Z',
            'rps': {'id': 77, 'number': 2094379153},
            'emitter': {'id': 13, 'social_reason': u'Empresa de Testes Ltda ME'},
            'from_status': None,
            'id': 289,
            'to_status': u'created',
            'token': u'DD00027F4A76E4B79209ACBFBC72F68E'
        }
        self.assertEqual(events[0].resource_data, first_event)

        second_event = {
            'account': {'id': 56, 'name': u'python-emites'},
            'date': u'2014-11-11T18:35:23.680Z',
            'rps': {'id': 77, 'number': 2094379153},
            'emitter': {'id': 13, 'social_reason': u'Empresa de Testes Ltda ME'},
            'from_status': u'created',
            'id': 290,
            'to_status': u'scheduled',
            'token': u'DD00027F4A76E4B79209ACBFBC72F68E'
        }
        self.assertEqual(events[1].resource_data, second_event)

    def test_nfses_have_a_status(self):
        with use_emites_cassette('nfse/get_from_this_account'):
            nfse = self.api_client.nfse.get(77)

        with use_emites_cassette('nfse/status'):
            nfse_status = nfse.status()

        self.assertTrue(isinstance(nfse_status, api_toolkit.entities.Resource))
        expected_status = {
            'description': u'Agendado o processamento da NFSe',
            'environment': u'sandbox',
            'id': 77,
            'mirror_url': None,
            'nfse_errors': [],
            'nfse_key': None,
            'nfse_number': None,
            'number': 2094379153,
            'pdf_url': None,
            'status': u'scheduled',
            'xml_url': None
        }
        self.assertEqual(nfse_status.resource_data, expected_status)

    def test_scheduled_nfses_cannot_be_cancelled(self):
        with use_emites_cassette('nfse/get_from_this_account'):
            nfse = self.api_client.nfse.get(77)

        with use_emites_cassette('nfse/cancel_scheduled'):
            self.assertRaises(requests.HTTPError, nfse.cancel)

    def test_scheduled_nfses_have_no_mirror(self):
        with use_emites_cassette('nfse/get_from_this_account'):
            nfse = self.api_client.nfse.get(77)

        with use_emites_cassette('nfse/has_no_mirror_when_scheduled'):
            self.assertRaises(requests.HTTPError, nfse.mirror)

    def test_scheduled_nfses_have_no_xml(self):
        with use_emites_cassette('nfse/get_from_this_account'):
            nfse = self.api_client.nfse.get(77)

        with use_emites_cassette('nfse/has_no_xml_when_scheduled'):
            self.assertRaises(requests.HTTPError, nfse.xml)

    def test_scheduled_nfses_have_no_pdf(self):
        with use_emites_cassette('nfse/get_from_this_account'):
            nfse = self.api_client.nfse.get(77)

        with use_emites_cassette('nfse/has_no_pdf_when_scheduled'):
            self.assertRaises(requests.HTTPError, nfse.pdf)

    def test_nfse_has_constants(self):
        with use_emites_cassette('nfse/constants'):
            constants = self.api_client.nfse.constants

        self.assertEqual(sorted(constants.keys()), sorted([
            'neighborhood_type',
            'operation_nature',
            'rps_situation',
            'rps_type',
            'special_regime',
            'status',
            'street_type',
            'taker_special_situation',
        ]))


class NfseConstantsTest(unittest.TestCase):

    def setUp(self):
        with use_emites_cassette('collections_options'):
            self.api_client = Emites(**APP_CREDENTIALS)

    def test_neighborhood_types(self):
        with use_emites_cassette('nfse/constants'):
            constants = self.api_client.nfse.constants

        self.assertEqual(constants['neighborhood_type'], {
            'COM': u'Comercial', 'IND': u'Industrial', 'RED': u'Residencial'
        })

    def test_operation_nature(self):
        with use_emites_cassette('nfse/constants'):
            constants = self.api_client.nfse.constants

        self.assertEqual(constants['operation_nature'], {
            '1': u'Tributação no munic\xedpio',
            '2': u'Tributação fora do munic\xedpio',
            '3': u'Isenção',
            '4': u'Imune',
            '5': u'Exigibilidade suspensa por decisão judicial',
            '6': u'Exigibilidade suspensa por procedimento Administrativo'
        })

    def test_rps_situation(self):
        with use_emites_cassette('nfse/constants'):
            constants = self.api_client.nfse.constants

        self.assertEqual(constants['rps_situation'], {
            '1': u'Normal', '2': u'Cancelado', '3': u'Extraviada'
        })

    def test_rps_type(self):
        with use_emites_cassette('nfse/constants'):
            constants = self.api_client.nfse.constants

        self.assertEqual(constants['rps_type'], {
            '1': u'RPS', '2': u'Nota Fisca Conjugada', '3': u'Cupom Tipo Padrão'
        })

    def test_special_regime(self):
        with use_emites_cassette('nfse/constants'):
            constants = self.api_client.nfse.constants

        self.assertEqual(constants['special_regime'], {
            '1': u'Microempresa Municipal',
            '2': u'Estimativa',
            '3': u'Sociedade de Profissionais',
            '4': u'Cooperativa',
            '5': u'MEI - Microempresário Individual',
            '6': u'ME EPP - Simples Nacional'
        })

    def test_status(self):
        with use_emites_cassette('nfse/constants'):
            constants = self.api_client.nfse.constants

        self.assertEqual(constants['status'], {
            'accepted': u'Processado pela Sefaz',
            'cancelled': u'Cancelado pela Sefaz',
            'processing': u'Processando NFSe junto a Sefaz',
            'rejected': u'Rejeitado pela Sefaz',
            'scheduled': u'Agendado o processamento da NFSe'
        })

    def test_street_type(self):
        with use_emites_cassette('nfse/constants'):
            constants = self.api_client.nfse.constants

        self.assertEqual(constants['street_type'], {
            'ALM': u'Alameda',
            'AVN': u'Avenida',
            'BEC': u'Beco',
            'BLV': u'Boulevard',
            'CAM': u'Caminho',
            'CAS': u'Cais',
            'CMP': u'Campo',
            'ESC': u'Escada',
            'ETR': u'Estrada',
            'FAV': u'Favela',
            'FAZ': u'Fazendo',
            'FLT': u'Floresta',
            'ILH': u'Ilha',
            'JRD': u'Jardim',
            'LAD': u'Ladeira',
            'LRG': u'Largo',
            'LTM': u'Loteamento',
            'LUG': u'Lugar',
            'MRR': u'Morro',
            'PAS': u'Passeio',
            'PQE': u'Parque',
            'PRA': u'Praia',
            'PRC': u'Praça',
            'REC': u'Recanto',
            'ROD': u'Rodovia',
            'RUA': u'Rua',
            'SRV': u'Servidão',
            'TRV': u'Travessa',
            'VIA': u'Via',
            'VIL': u'Vila'
        })

    def test_taker_special_situation(self):
        with use_emites_cassette('nfse/constants'):
            constants = self.api_client.nfse.constants

        self.assertEqual(constants['taker_special_situation'], {
            '0': u'Outros',
            '1': u'SUS',
            '2': u'Órgão do Poder Executivo',
            '3': u'Bancos',
            '4': u'Coméricio/Industria',
            '5': u'Poder Legislativo/Judiciário'
        })


class BatchesTest(WithFrozenTime):

    def setUp(self):
        super(BatchesTest, self).setUp()
        with use_emites_cassette('collections_options'):
            self.api_client = Emites(**APP_CREDENTIALS)

        with use_emites_cassette('emitters/get_from_this_account'):
            self.emitter = self.api_client.emitters.get(13)

        self.post_data = {
            'emitter_id': self.emitter.id,
            'name': u'Lote de teste da API'
        }

    def _create_empty_batch(self):
        self.post_data['name'] = u'{0} (vazio)'.format(self.post_data['name'])
        with use_emites_cassette('batches/create_empty_batch'):
            empty_batch = self.api_client.batches.create(**self.post_data)

        return empty_batch

    def test_batches_are_a_collection(self):
        self.assertTrue(isinstance(self.api_client.batches, api_toolkit.Collection))

    def test_batches_are_iterable(self):
        with use_emites_cassette('batches/list'):
            batches = [item for item in self.api_client.batches.all()]

    def test_batches_can_be_created(self):
        with use_emites_cassette('batches/create'):
            batch = self.api_client.batches.create(**self.post_data)

        self.assertEqual(batch.id, 24)
        self.assertEqual(batch.emitter_id, self.emitter.id)
        self.assertEqual(batch.name, self.post_data['name'])

    def test_batches_can_be_filtered_by_status(self):
        with use_emites_cassette('batches/filter_by_status'):
            batches = list(self.api_client.batches.all(status='created'))

        self.assertEqual(len(batches), 1)
        self.assertEqual(batches[0].id, 24)

    def test_batches_can_be_filtered_by_emitter(self):
        with use_emites_cassette('batches/filter_by_emitter'):
            batches = list(self.api_client.batches.all(emitter_id=self.emitter.id))

        self.assertEqual(len(batches), 1)
        self.assertEqual(batches[0].id, 24)

    def test_batches_from_other_emitters_cannot_be_seen(self):
        with use_emites_cassette('batches/filter_by_other_emitter'):
            batches = list(self.api_client.batches.all(emitter_id=11))

        self.assertEqual(len(batches), 0)

    def test_batches_can_be_filtered_by_name(self):
        with use_emites_cassette('batches/filter_by_name'):
            batches = list(self.api_client.batches.all(name=self.post_data['name']))

        self.assertEqual(len(batches), 1)
        self.assertEqual(batches[0].id, 24)

    def test_creation_without_name_fails(self):
        del(self.post_data['name'])
        with use_emites_cassette('batches/create_without_name'):
            self.assertRaises(requests.HTTPError, self.api_client.batches.create, **self.post_data)

    def test_creation_without_emitter_id_fails(self):
        del(self.post_data['emitter_id'])
        with use_emites_cassette('batches/create_without_emitter_id'):
            self.assertRaises(requests.HTTPError, self.api_client.batches.create, **self.post_data)

    def test_get_batch_from_another_account_fails(self):
        with use_emites_cassette('batches/get_from_another_account'):
            self.assertRaises(requests.HTTPError, self.api_client.batches.get, 11)

    def test_get_batch_from_this_account_works(self):
        with use_emites_cassette('batches/get_from_this_account'):
            batch = self.api_client.batches.get(24)

        self.assertEqual(batch.emitter_id, self.post_data['emitter_id'])
        self.assertEqual(batch.id, 24)

    def test_batches_cannot_be_updated(self):
        with use_emites_cassette('batches/get_from_this_account'):
            batch = self.api_client.batches.get(24)

        self.assertRaises(ValueError, batch.save)

    def test_batches_cannot_be_deleted(self):
        with use_emites_cassette('batches/get_from_this_account'):
            batch = self.api_client.batches.get(24)

        self.assertRaises(ValueError, batch.delete)

    def test_batch_nfses_are_a_collection(self):
        with use_emites_cassette('batches/get_from_this_account'):
            batch = self.api_client.batches.get(24)

        self.assertTrue(isinstance(batch.nfse, api_toolkit.Collection))

    def test_batch_nfses_are_iterable(self):
        with use_emites_cassette('batches/get_from_this_account'):
            batch = self.api_client.batches.get(24)

        with use_emites_cassette('batches/nfse/list'):
            nfses = [item for item in batch.nfse.all()]

    def test_batches_have_its_own_class(self):
        with use_emites_cassette('batches/get_from_this_account'):
            batch = self.api_client.batches.get(24)

        self.assertTrue(isinstance(batch, Batch))

    def test_batches_have_a_history(self):
        with use_emites_cassette('batches/get_from_this_account'):
            batch = self.api_client.batches.get(24)

        with use_emites_cassette('batches/history'):
            events = [item for item in batch.history.all()]

        self.assertEqual(len(events), 1)
        expected_event = {
            'account': {'id': 56, 'name': u'python-emites'},
            'batch': {'id': 24, 'name': u'Lote de teste da API'},
            'date': u'2014-11-11T20:17:36.441Z',
            'emitter': {'id': 13, 'social_reason': u'Empresa de Testes Ltda ME'},
            'from_status': None,
            'id': 299,
            'to_status': u'created',
            'token': u'DD00027F4A76E4B79209ACBFBC72F68E'
        }
        self.assertEqual(events[0].resource_data, expected_event)

    def test_batches_can_be_sent(self):
        with use_emites_cassette('batches/get_from_this_account'):
            batch = self.api_client.batches.get(24)
        self.assertEqual(batch.status, 'created')

        with use_emites_cassette('batches/send'):
            sent_batch = batch.send()
        self.assertEqual(sent_batch.status, 'scheduled')
        self.assertTrue(isinstance(sent_batch, Batch))

    def test_empty_batches_cannot_be_sent(self):
        empty_batch = self._create_empty_batch()
        self.assertEqual(empty_batch.status, 'created')

        with use_emites_cassette('batches/send_empty_batch'):
            self.assertRaises(requests.HTTPError, empty_batch.send)

    def test_sent_batches_cannot_be_cancelled(self):
        with use_emites_cassette('batches/get_from_this_account'):
            batch = self.api_client.batches.get(24)
        self.assertEqual(batch.status, 'created')

        with use_emites_cassette('batches/send'):
            sent_batch = batch.send()
        self.assertEqual(sent_batch.status, 'scheduled')

        with use_emites_cassette('batches/cancel_sent_batch'):
            self.assertRaises(requests.HTTPError, sent_batch.cancel)

    def test_empty_batches_cannot_be_cancelled(self):
        empty_batch = self._create_empty_batch()
        self.assertEqual(empty_batch.status, 'created')

        with use_emites_cassette('batches/cancel_empty_batch'):
            self.assertRaises(requests.HTTPError, empty_batch.cancel)
