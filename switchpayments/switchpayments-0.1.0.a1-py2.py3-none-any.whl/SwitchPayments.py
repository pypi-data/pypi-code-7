import requests
import json


class SwitchPayments:
    environment = None
    merchant_id = None
    private_key = None

    SANDBOX_ENVIRONMENT = "http://192.168.1.9:8001/v1/"

    def __init__(self, environment, merchant_id, private_key):
        SwitchPayments.environment = environment
        SwitchPayments.merchant_id = merchant_id
        SwitchPayments.private_key = private_key

    class Card:
        def __init__(self):

            pass

        @staticmethod
        def create(request_token):

            url = SwitchPayments.environment + "cards/"
            payload = {"card": request_token}
            json_payload = json.dumps(payload)

            r = requests.post(url, json_payload, auth=(SwitchPayments.merchant_id, SwitchPayments.private_key))

            response = r.json()

            try:
                return response["id"]
            except KeyError:
                return response


    class Customer:
        def __init__(self):
            pass

        @staticmethod
        def create(name, email, card, description=None):

            url = SwitchPayments.environment + "customers/"

            payload = {"name": name,
                       "email": email,
                       "description": description,
                       "card": card}

            json_payload = json.dumps(payload)

            r = requests.post(url, json_payload, auth=(SwitchPayments.merchant_id, SwitchPayments.private_key))

            response = r.json()

            print r.text

            try:
                return response["id"]
            except KeyError:
                return response



    class Payment:
        def __init__(self):
            pass

        @staticmethod
        def authorize(amount, currency, card=None, customer=None, description=None):
            payment_id = SwitchPayments.Payment.__create_payment(amount, currency, card, customer, description)
            print payment_id
            payment_id = SwitchPayments.Payment.__authorize_payment(payment_id)
            return payment_id

        @staticmethod
        def __create_payment(amount, currency, card=None, customer=None, description=None):
            url = SwitchPayments.environment + "payments/"

            payload = {"amount": amount,
                       "currency": currency,
                       "description": description}

            if card:
                payload["card"] = card

            if customer:
                payload["customer"] = customer

            json_payload = json.dumps(payload)

            r = requests.post(url, json_payload, auth=(SwitchPayments.merchant_id, SwitchPayments.private_key))

            response = r.json()

            try:
                return response["id"]
            except KeyError:
                return response



        @staticmethod
        def __authorize_payment(payment_id):

            url = SwitchPayments.environment + "payments/" + str(payment_id) + "/authorize"
            json_payload = json.dumps({})

            r = requests.post(url, json_payload, auth=(SwitchPayments.merchant_id,
                                                       SwitchPayments.private_key))

            response = r.json()

            try:
                return response["id"]
            except KeyError:
                return response

            pass


        @staticmethod
        def capture(transaction_id):

            url = SwitchPayments.environment + "payments/" + str(transaction_id) + "/capture/"

            json_payload = json.dumps({})

            r = requests.post(url, json_payload, auth=(SwitchPayments.merchant_id, SwitchPayments.private_key))
            response = r.json()

            try:
                return response["id"]
            except KeyError:
                return response

        @staticmethod
        def void(transaction_id):

            url = SwitchPayments.environment + "payments/" + str(transaction_id) + "/void/"

            json_payload = json.dumps({})

            r = requests.post(url, json_payload, auth=(SwitchPayments.merchant_id, SwitchPayments.private_key))
            response = r.json()

            try:
                return response["id"]
            except KeyError:
                return response


        @staticmethod
        def refund(transaction_id, amount):

            url = SwitchPayments.environment + "payments/" + str(transaction_id) + "/refund/"

            json_payload = json.dumps({"amount": amount})

            r = requests.post(url, json_payload, auth=(SwitchPayments.merchant_id, SwitchPayments.private_key))
            response = r.json()

            try:
                return response["id"]
            except KeyError:
                return response









