class SwitchPayments:
    def __init__(self, environment, merchant_id, private_key):
        self.environment = environment
        self.merchant_id = merchant_id
        self.private_key = private_key

    class Card:
        def __init__(self):
            pass

        @staticmethod
        def create(request_token):
            return "multi_use_card_token"

    class Payment:
        def __init__(self):
            pass

        @staticmethod
        def authorize(amount, currency, card):
            return "transaction_id"

        @staticmethod
        def capture(transaction_id):
            return "success"

        @staticmethod
        def void(transaction_id):
            return "success"





