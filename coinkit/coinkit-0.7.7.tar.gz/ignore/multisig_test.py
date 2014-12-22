from pybitcointools import mktx as make_tx
from pybitcointools import mk_multisig_script as make_multisig_script
from pybitcointools import sign as sign_tx
from pybitcointools import p2sh_scriptaddr as p2sh_script_address
from coinkit import BitcoinPrivateKey, BitcoinPublicKey

from coinkit.transactions import get_unspents

def create_unsigned_multisig_tx(hex_public_keys, inputs, send_amount, change_address,
                                tx_fee=1000, m=2, n=3):
    public_keys = [BitcoinPublicKey(k) for k in hex_public_keys]
    addresses = [public_key.address() for public_key in public_keys]

    multisig_script = make_multisig_script(hex_public_keys, m, n)
    multisig_address = p2sh_script_address(multisig_script)

    total_in = sum([input['value'] for input in inputs])
    change_amount = total_in - send_amount - tx_fee

    unsigned_tx = make_tx(
        inputs,
        [multisig_address + ':' + str(send_amount), change_address + ':' + str(change_amount)]
    )

    return unsigned_tx

def create_unsigned_address_tx(receive_address, inputs, send_amount,
                               change_address, tx_fee=1000):
    #output_script = mk_pubkey_script(receive_address)
    total_in = sum([input['value'] for input in inputs])
    change_amount = total_in - send_amount - tx_fee
    unsigned_tx = make_tx(
        inputs,
        [receive_address + ':' + str(send_amount), change_address + ':' + str(change_amount)]
    )
    return unsigned_tx

def get_inputs_formatted_for_pybitcointools(address, api='chain', auth=None):
    if api == 'chain':
        unspents = get_unspents(address, auth=auth)
    else:
        raise Exception('API not supported')

    return [{
        'output': unspent['transaction_hash'] + ':' + str(unspent['output_index']),
        'value': unspent['value']
    } for unspent in unspents]

def main():
    chain_auth = ('e21be6b69908544615b1d00f2c333c13', 'ef4c57ddb65cb5997c9f5e25b09cf520')
    
    #m = 2
    #n = 3
    send_amount = 1000

    spend_hex_private_key = '0baab1b8c6e1fef90ff9d683d2d3d4c716752966dc0ffb8886a4bff211de1adb'
    spend_address = BitcoinPrivateKey(spend_hex_private_key).public_key().address()

    inputs = get_inputs_formatted_for_pybitcointools(spend_address, auth=chain_auth)

    #multisig_private_keys = [BitcoinPrivateKey() for i in range(n)]
    #hex_multisig_private_keys = [k.to_hex() for k in multisig_private_keys]
    #print hex_multisig_private_keys
    #multisig_public_keys = [k.public_key() for k in multisig_private_keys]
    #hex_multisig_public_keys = [k.to_hex() for k in multisig_public_keys]

    unsigned_address_tx = create_unsigned_address_tx(
        '1BuD5zX3hgW7p74eouLWFWTgsaNpEo9mTG', inputs, send_amount, spend_address
    )
    print unsigned_address_tx

    #unsigned_multisig_tx = create_unsigned_multisig_tx(
    #    hex_multisig_public_keys, inputs, send_amount, spend_address, m=m, n=n)
    #print unsigned_multisig_tx
    #signed_multisig_tx = sign_tx(unsigned_multisig_tx, 0, spend_hex_private_key)
    #print signed_multisig_tx

    #print chain_com.send_transaction(signed_multisig_tx, auth=chain_auth)

main()
