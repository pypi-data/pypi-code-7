import os.path
from zozol import to_pem


def here(fname):
    dirname, _ = os.path.split(__file__)
    return os.path.join(dirname, fname)


def test_pem():
    x509_data = open(here('signed1.x509'), 'rb').read()
    p509_data = open(here('signed1.x509.pem'), 'r').read()
    pem_data = to_pem(x509_data, 'certificate')
    assert pem_data == p509_data
