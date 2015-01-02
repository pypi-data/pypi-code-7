from __future__ import absolute_import
from chain import SDKVersion
import requests
from bitcoin.core.key import CECKey
from bitcoin.base58 import decode, encode
import hashlib
from binascii import unhexlify

def request(URI, operation='GET', data=""):
    headers = {
        'User-Agent': "chain-python v" + SDKVersion,
        'Accept-Encoding': 'GZIP',
        'Content-Type': 'application/json',
        'Accept': '*/*'
    }
    assert operation in ['GET','POST']
    if operation == 'GET':
        r = requests.get(URI, data=data, headers=headers, timeout=10, verify=True, allow_redirects=False)
    elif operation == 'POST':
        r = requests.post(URI, data=data, headers=headers, timeout=10, verify=True, allow_redirects=False)
    return r.text

def convertPrivateKeysToBinaryFormat(privateKeys, blockChain):
    """
    Accepts a list of privateKeys in either hex or WIF format.
    Returns a list of tuples where each tuple is (privKey, compressed)
        where `privKey` is the private key in binary format
        and `compressed` is a bool indicating whether or not the corresponding public key is compressed.
    """
    privateKeysBinary = []
    for privateKey in privateKeys:
        privateKeysBinary.append(convertPrivateKeyToBinaryFormat(privateKey, blockChain))
    return privateKeysBinary

def convertPrivateKeyToBinaryFormat(privateKey, blockChain):
    """
    Accepts a single privateKey in either hex or WIF format.
    Returns a single tuple where the tuple is (privKey, compressed)
        where `privKey` is the private key in binary format
        and `compressed` is a bool indicating whether or not the corresponding public key is compressed.
    """
    if len(privateKey) == 64: # if the key is in hex already.. 
        # Assume that it is not for a compressed pubkey
        return (unhexlify(privateKey), False)
    else: # if the key is probably not in hex already then
        # assume that the private key is in wallet-import-format and try to decode it.
        # decodeWalletImportFormat will check the checksum and whatnot and throw exceptions
        # if something seems wrong.
        return decodeWalletImportFormat(privateKey, blockChain)
    
                                     
def decodeWalletImportFormat(walletImportFormatString, blockChain):
    """
    Returns a tuple: (privKey, compressed)
        where `privKey` is the private key in binary format
        and `compressed` is a bool indicating whether or not the corresponding public key is compressed 
        
    This function currently supports bitcoin mainnet and testnet.
    """
    fullString = decode(walletImportFormatString)
    privkey = fullString[:-4]
    if fullString[-4:] != hashlib.sha256(hashlib.sha256(privkey).digest()).digest()[:4]:
        raise Exception("When trying to decode one of your private keys, the wallet-import-format checksum was wrong.")
    
    #checksum passed. 
    
    # If you aren't very familiar with Wallet import format then this is going to be pretty confusing
    # https://en.bitcoin.it/wiki/Wallet_import_format
    
    if blockChain == 'bitcoin':
        if privkey[0:1] != b'\x80': # If the first byte isn't hex 80
            raise Exception("When trying to decode one of your private keys, the checksum passed but the key doesn\'t begin with hex 80.")
        # The first character must be a 5 for uncompressed keys OR K or L for compressed keys
        if walletImportFormatString[0] == "5":
            compressed = False
        elif walletImportFormatString[0] in ["K","L"]:
            compressed = True
            # We need to drop the last byte which should be \x01
            if privkey[33:34] != b'\x01':
                raise Exception("Your decoded compressed WIF key did not end with a \x01 byte.")
            privkey = privkey[:-1]
        else:
            raise Exception("In mainnet mode, the private key must start with 5, K, or L. Or it must be in Hex.")
        return (privkey[1:], compressed)
    elif blockChain.startswith('testnet'):
        if privkey[0:1] != b'\xEF':
            raise Exception("When trying to decode one of your private keys, the checksum passed but the key doesn\'t begin with hex EF.")
        if walletImportFormatString[0] == "9":
            compressed = False
        elif walletImportFormatString[0] == "c":
            compressed = True
            # We need to drop the last byte which should be \x01
            if privkey[33:34] != b'\x01':
                raise Exception("Your decoded compressed WIF key did not end with a \x01 byte.")
            privkey = privkey[:-1]
        else:
            raise Exception("In testnet mode, the private key must start with 9 or c. Or it must be in Hex.")
        return (privkey[1:], compressed)
    else:
        raise Exception("'blockChain' argument is not set properly.")

def generateKeyCollection(privateKeys, blockChain):
    """
    return a dictionary where the keys of the dictionary are bitcoin addresses
    and the values of the dictionary are tuples: (privKey, compressed)
        where `privKey` is the private key in binary format
        and `compressed` is a bool indicating whether or not the corresponding public key is compressed 
    
    Parameters:
    privateKeys must be a list tuples: (privKey, compressed)
        where `privKey` is the private key in binary format
        and `compressed` is a bool indicating whether or not the corresponding public key is compressed 
    blockChain must be either 'bitcoin' or start with 'testnet'
    """
    keyCollection = {}
    for privateKey, compressed in privateKeys:
        address = deriveAddress(privateKey, compressed, blockChain)
        keyCollection[address] = (privateKey, compressed)
    return keyCollection
        
        
def deriveAddress(privateKey, compressed, blockChain):
    """
    Turn a private key into an address.
    privateKey must be in binary format.
    """
    privKey = CECKey()
    privKey.set_secretbytes(privateKey)
    privKey.set_compressed(compressed)
    publicKey = privKey.get_pubkey()
    hash1 = hashlib.sha256(publicKey).digest()
    
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(hash1)
    ripe = ripemd160.digest()

    if blockChain == 'bitcoin':
        ripeWithNetworkPrefix = b'\x00' + ripe
    elif blockChain.startswith('testnet'):
        ripeWithNetworkPrefix = b'\x6F' + ripe
    else: 
        raise Exception("'blockChain' parameter is not set correctly")

    checksum = hashlib.sha256(hashlib.sha256(
        ripeWithNetworkPrefix).digest()).digest()[:4]
    binaryBitcoinAddress = ripeWithNetworkPrefix + checksum
    numberOfZeroBytesOnBinaryBitcoinAddress = 0
    while binaryBitcoinAddress[0:1] == b'\x00': # while the first byte is null
        numberOfZeroBytesOnBinaryBitcoinAddress += 1
        binaryBitcoinAddress = binaryBitcoinAddress[1:] # take off the first byte
    base58encoded = encode(binaryBitcoinAddress) # encode into base58
    return "1" * numberOfZeroBytesOnBinaryBitcoinAddress + base58encoded
        