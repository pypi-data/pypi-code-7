import requests as r

try:
    import simplejson as json
except ImportError:
    import json


from .config import BASE_URL


class User(object):

    def __init__(self, headers):
        self.headers = headers

    def get(self, params):
        headers = self.headers
        id = params.get('id', None)
        email = params.get('email', None)
        if id:
            response = r.get('%s/users/%s' % (BASE_URL, id), headers=headers)
        elif email:
            response = r.get('%s/admin-get-user-token/%s' % (BASE_URL, email),
                             headers=headers)
        else:
            return json.dumps({'response_text': 'Check your parameters'})
        return response.json()

    def create(self, name, phone, email, options):
        body = options['body'] if 'body' in options else {}
        body['name'] = name
        body['phone'] = phone
        body['email'] = email
        data = json.dumps(body)
        headers = self.headers
        response = r.post('%s/users/' % BASE_URL, data=data, headers=headers)
        return response.json()


class PaymentSettings(object):
    def __init__(self, headers):
        self.headers = headers

    def list(self):
        headers = self.headers
        response = r.get('%s/payments' % BASE_URL, headers=headers)
        return response.json()


class Invoice(object):

    def __init__(self, headers):
        self.headers = headers

    def get(self, ref):
        headers = self.headers
        response = r.get('%s/invoices/%s' % (BASE_URL, ref), headers=headers)
        return response.json()

    def create(self, total, delivery_cost, ref, first_name, return_url,
               items=[], options={}):
        body = options['body'] if 'body' in options else {}
        body['total'] = total
        body['delivery_cost'] = delivery_cost
        body['ref'] = ref
        body['first_name'] = first_name
        body['items'] = items
        body['return_url'] = return_url
        data = json.dumps(body)
        headers = self.headers
        response = r.post('%s/invoices/' % BASE_URL, data=data,
                          headers=headers)
        return response.json()

    def list(self):
        response = r.get('%s/invoices/' % BASE_URL, headers=self.headers)
        return response.json()

    def status(self, ref):
        response = r.get('%s/invoices/%s/status' % (BASE_URL, ref),
                         headers=self.headers)
        return response.json()
