# -*- coding: utf-8 -*-
import os
from vcr import VCR

__all__ = [
    'use_cassette',
    'APP_CREDENTIALS', 'TEST_EMITTER',
    'TEST_SERVICE_VALUE', 'TEST_NFSE'
]

def use_cassette(*args, **kwargs):
    return VCR(
        cassette_library_dir = os.path.join(os.path.dirname(__file__), 'cassettes', 'emites'),
        match_on = ['url', 'method', 'headers', 'body'],
        record_mode = 'once',
    ).use_cassette(*args, **kwargs)


APP_CREDENTIALS = {
    'host': 'https://sandbox.emites.com.br',
    'token': '685167D4190D94A94619487A106561E7',
}

CERTIFICATE = {
    'binary_path': 'certs/test.pfx',
    'text_path': 'certs/test.base64',
    'password': 'associacao',
}

with open(os.path.join(os.path.dirname(__file__), CERTIFICATE['text_path']), 'r') as cert_handle:
    TEST_EMITTER = {
        'email': 'financeiro@python-emites.test',
        'cnpj': '91762868000184',
        'fancy_name': 'Empresa de Testes',
        'social_reason': 'Empresa de Testes Ltda ME',
        'state_inscription': 'ISENTO',
        'city_inscription': '00000000',
        'state': 'RJ',
        'city': 'Rio de Janeiro',
        'neighborhood': 'Centro',
        'street_type': 'RUA',
        'street': 'dos testes',
        'number': 42,
        'zip_code': '20011020',
        'phone': '21000000000',
        'certificate': cert_handle.read(),
        'password': CERTIFICATE['password'],
    }

TEST_TAKER = {
    'cnpj': '91762868000184',
    'fancy_name': 'Empresa de Testes',
    'social_reason': 'Empresa de Testes Ltda ME',
    'city_inscription': '00000000',
    'state_inscription': 'ISENTO',
    'address': {
        'state': 'RJ',
        'city_code': 3304557,
        'city': 'Rio de Janeiro',
        'street_type': 'RUA',
        'street': 'dos testes',
        'number': 42,
        'neighborhood_type': 'COM',
        'neighborhood': 'Centro',
        'zip_code': '20011020',
        'country_code': '01058',
        'country': 'Brasil',
        'country_abbreviation': 'BR',
    },
    'contact': {
        'phone': '21000000000',
        'email': 'financeiro@python-emites.test',
    }
}

TEST_SERVICE_VALUE = {
    'emitter_id': '',
    'name': u'Testes da api do emites',
    'service_amount': '99.99',
    'iss_percentage': '5.00',
}

TEST_NFSE = {
    'emitter_id': '',
    'serie': 'TESTE',
    'service_values': {
        'id': '',
        'service_amount': '99.99',
        'iss_percentage': '5.00',
        'iss_amount': '4.99',
        'deduction_amount': '0.00',
        'discount_conditioning_amount': '0.00',
        'calculation_base': '99.99',
        'nfse_liquid_amount': '99.99',
        'service_item_code': '0105',
        'city_tax_code': '010501',
        'cnae_code': '6201-5',
        'city_code': 3304557,
        'description': u'Testes da api do emites',
    }
}
