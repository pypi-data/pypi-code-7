from nacl.public import PrivateKey, PublicKey, Box
from nacl.signing import SigningKey, VerifyKey
from nacl.utils import random
from nacl.hash import sha256


def nacl_sha256(text):
    return sha256(text).decode('hex')


def nacl_random(size):
    return random(size)


def nacl_nonce():
    return random(Box.NONCE_SIZE)


def nacl_box(pub_key, secret=None):
    pri_key = PrivateKey(secret) if secret else PrivateKey.generate()
    pub_key = PublicKey(pub_key)
    return Box(pri_key, pub_key), pri_key, pub_key


def nacl_sign(msg, seed=None):
    key = SigningKey(seed) if seed else SigningKey.generate()
    return key.sign(msg), key.verify_key


def nacl_verify(signed, key):
    return VerifyKey(key).verify(signed)
