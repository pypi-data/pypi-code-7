# print send_from_address_to_address('1BuD5zX3hgW7p74eouLWFWTgsaNpEo9mTG', '1BuD5zX3hgW7p74eouLWFWTgsaNpEo9mTG')
# 7790fa0ed25378512caa31aa5aad60e603868c09


"""

def standard_tx_fee():
    return 1000

def create_unsigned_tx(inputs, outputs,
                       fee=standard_tx_fee(), lock_time=0, version=1):
    pass

def sign_tx(unsigned_tx, private_keys):
    pass

def create_signed_tx(inputs, outputs, private_keys=[],
                     fee=standard_tx_fee(), lock_time=0, version=1):
    pass

class Input(object):
    def __init__(self, transaction_hash, output_index, script):
        self.transaction_hash = transaction_hash
        self.output_index = output_index
        self.script = script
        self.sequence = UINT_MAX

    def __str__(self):
        return self.to_dict()

    def to_dict(self):
        return {
            "transaction_hash": self.transaction_hash,
            "output_index": self.output_index,
            "script": self.script,
            "sequence": self.sequence
        }

    def serialize(self):
        return serialize_input(self.to_dict())

class Output(object):
    def __init__(self, value, script):
        self.value = value
        self.script = script

    def to_dict(self):
        return {
            "value": self.value,
            "script": self.script
        }

    def serialize(self):
        return serialize_output(self.to_dict())

"""

