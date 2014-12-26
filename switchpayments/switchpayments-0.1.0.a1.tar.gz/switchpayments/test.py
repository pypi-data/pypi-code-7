# -*- coding: utf-8 -*-

from SwitchPayments import SwitchPayments

sw = SwitchPayments(environment=SwitchPayments.SANDBOX_ENVIRONMENT,
                    merchant_id=1,
                    private_key=3)

multi_use_card_token = sw.Card.create("a750479780ab551fd17f33165ed6695887617763549d9910")

print multi_use_card_token

transaction_id = sw.Payment.authorize(amount=12,
                                      currency="EUR",
                                      card=multi_use_card_token)


#response = sw.Payment.void(transaction_id)

response = sw.Payment.capture(transaction_id)
response = sw.Payment.refund(transaction_id, 12)


# customer_id = sw.Customer.create(name="António Fonseca4",
#                                  email="antoniof4@gmail.com",
#                                  card="c1fff07770f5d12981ac30d705b214e535dbf7b3549d9837")

# print "custumer_id: " + customer_i d

# transaction_id = sw.Payment.authorize(amount=12,
#                                       currency="EUR",
# 2                                      customer=customer_id)


print transaction_id

