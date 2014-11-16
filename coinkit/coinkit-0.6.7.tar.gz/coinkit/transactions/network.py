# -*- coding: utf-8 -*-
"""
    Coinkit
    ~~~~~

    :copyright: (c) 2014 by Halfmoon Labs
    :license: MIT, see LICENSE for more details.
"""

from binascii import hexlify, unhexlify
from pybitcointools import sign as sign_transaction

from ..services import blockchain_info, chain_com
from ..privatekey import BitcoinPrivateKey
from .serialize import serialize_transaction, make_pay_to_address_outputs, \
    make_op_return_outputs
from .utils import STANDARD_FEE

""" Note: for functions that take in an auth object, here are some examples
    for the various APIs available:
    
    blockchain.info: auth=(api_key, None)
    chain.com: auth=(api_key_id, api_key_secret)
"""

def get_unspents(address, api='blockchain.info', auth=None):
    """ Gets the unspent outputs for a given address.
    """
    if api == 'blockchain.info':
        return blockchain_info.get_unspents(address, auth=auth)
    elif api == 'chain.com':
        return chain_com.get_unspents(address, auth=auth)
    else:
        raise Exception('API not supported.')

def broadcast_transaction(hex_transaction, api='chain.com', auth=None):
    """ Dispatches a raw hex transaction to the network.
    """
    if api == 'chain.com':
        return chain_com.broadcast_transaction(hex_transaction, auth=auth)
    elif api == 'blockchain.info':
        return blockchain_info.broadcast_transaction(hex_transaction, auth=auth)
    else:
        raise Exception('API not supported.')

def send_to_address(recipient_address, amount, sender_private_key, auth,
                    api='chain.com', fee=STANDARD_FEE, change_address=None):
    """ Builds, signs, and dispatches a "send to address" transaction.
    """
    if not isinstance(sender_private_key, BitcoinPrivateKey):
        sender_private_key = BitcoinPrivateKey(sender_private_key)
    # determine the address associated with the supplied private key
    from_address = sender_private_key.public_key().address()
    # get the unspent outputs corresponding to the given address
    inputs = get_unspents(from_address, api=api, auth=auth)
    # get the change address
    if not change_address:
        change_address = from_address
    # create the outputs
    outputs = make_pay_to_address_outputs(recipient_address, amount, inputs,
                                          change_address, fee)
    # serialize the transaction
    unsigned_tx = serialize_transaction(inputs, outputs)
    # sign the unsigned transaction with the private key
    signed_tx = sign_transaction(unsigned_tx, 0, sender_private_key.to_hex())
    # dispatch the signed transction to the network
    response = broadcast_transaction(signed_tx, api=api, auth=auth)
    # return the response
    return response

def embed_data_in_blockchain(data, sender_private_key, auth, api='chain.com',
        fee=STANDARD_FEE, change_address=None, format='bin'):
    """ Builds, signs, and dispatches an OP_RETURN transaction.
    """
    if not isinstance(sender_private_key, BitcoinPrivateKey):
        sender_private_key = BitcoinPrivateKey(sender_private_key)
    # determine the address associated with the supplied private key
    from_address = sender_private_key.public_key().address()
    # get the unspent outputs corresponding to the given address
    inputs = get_unspents(from_address, api=api, auth=auth)
    # get the change address
    if not change_address:
        change_address = from_address
    # create the outputs
    outputs = make_op_return_outputs(data, inputs, change_address, format=format)
    # serialize the transaction
    unsigned_tx = serialize_transaction(inputs, outputs)
    # sign the unsigned transaction with the private key
    signed_tx = sign_transaction(unsigned_tx, 0, sender_private_key.to_hex())
    # dispatch the signed transction to the network
    response = broadcast_transaction(signed_tx, api=api, auth=auth)
    # return the response
    return response
